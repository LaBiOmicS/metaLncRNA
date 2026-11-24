# Imagens das ferramentas

As sete imagens são montadas do mesmo jeito: um diretório por ferramenta com `Dockerfile` e um
lançador `run-<ferramenta>`, que é o `ENTRYPOINT`. Toda imagem é **autocontida** (ferramenta,
dependências e arquivos de modelo) e traz rótulos OCI de proveniência (`org.opencontainers.image.*`,
`metalncrna.base`, `metalncrna.modified="false"`). **Nenhuma linha do código das ferramentas é
alterada**; os lançadores só fixam o diretório de trabalho.

## CPAT, CPC2, PLEK, RNAsamba (Bioconda)

A base é a imagem do BioContainers fixada por digest (`metalncrna.base`); as dependências não são
recompiladas. CPAT e RNAsamba recebem, via `ADD --checksum`, os modelos publicados pelos autores
(CPAT `prebuilt_models` @ v3.0.5; RNAsamba `data/full_length_weights.hdf5` e
`partial_length_weights.hdf5` @ 0.2.5). CPC2 e PLEK já trazem o modelo no pacote. O PLEK usa a
build py310 porque a build py312 está quebrada (`open(..., 'rU')`, removido no Python 3.11).

## CNCI, CPPred, LGC (Python 2.7, código dos autores)

O arquivo original fica versionado em `<ferramenta>/upstream/` e é conferido por SHA-256 durante o
build.

| Ferramenta | Origem | Arquivo upstream | SHA-256 | Ação de build |
|---|---|---|---|---|
| CNCI v2 | https://github.com/www-bioinfo-org/CNCI @ `745e2d1942f0fa6c061f5308fdc876de430a114f` (GPL-2.0) | `CNCI-745e2d1….tar.gz` | `5a0a6bb0ab2847e4b4b1159ab44c76806bc4816b08456a7dbc4ab3ad78289326` | compila o `libsvm-3.0` incluído, como manda o README (link estático, para rodar na glibc da imagem Python 2.7) |
| CPPred | http://www.rnabinding.com/CPPred/ (`CPPred.tar.gz`, 2018-05-17) | `CPPred.tar.gz` | `43a4eff80f5eeaa1f8266a51e38e3d288034cc36294e1d622faa1b3cb7ef4f06` | nenhuma; usa os binários `libsvm-3.22` do próprio pacote; `biopython==1.75` conforme instrução dos autores |
| LGC | https://ngdc.cncb.ac.cn/lgc/ (download "LGC-1.0.tar.gz", que é um RAR v4) | `LGC-1.0.rar` | `67cdbcbc6cbaabe17c71639f43c8277aad0be3466b6a6dfdb5865ddc9c55f9b6` | apenas extração |

Imagem base: `python:2.7.18-slim-buster@sha256:6c1ffdff…2363` (fixada por digest em cada Dockerfile).

## Por que os lançadores existem

- **CPPred** chama `../libsvm-3.22/svm-*` de forma relativa e grava `test.*`/`tmp*` no diretório
  corrente (e depois executa `rm tmp*`). O lançador copia a árvore para um diretório temporário
  próprio e roda a partir de `CPPred/bin`, como no README dos autores; assim o código não precisa
  ser alterado.
- **LGC** grava `ORF*.temp`/`top*.temp` no diretório corrente; roda num diretório temporário.
- **CNCI** escreve só em `<saída>/` e `<saída>.log`; o lançador apenas chama o script.

Os caminhos passados às ferramentas devem ser **absolutos**.

## Uso

```sh
docker build -t metalncrna/cppred:dev containers/cppred    # idem para as outras seis
docker run --rm --user $(id -u):$(id -g) -v $PWD:/data metalncrna/cppred:dev \
  -i /data/in.fa -hex /opt/CPPred/Hexamer/Human_Hexamer.tsv \
  -r /opt/CPPred/Human_Model/Human.range -mol /opt/CPPred/Human_Model/Human.model \
  -spe Human -o /data/cppred.txt
docker run --rm --user $(id -u):$(id -g) -v $PWD:/data metalncrna/lgc:dev /data/in.fa /data/lgc.txt
docker run --rm --user $(id -u):$(id -g) -v $PWD:/data metalncrna/cnci:dev -f /data/in.fa -o /data/cnci -m ve -p 4
# Apptainer: apptainer build cppred.sif docker-daemon://metalncrna/cppred:dev
```

## Validação (2026-11-17)

Amostra do conjunto de teste humano que vem dentro do pacote do CPPred (100 codificantes + 100 ncRNA):

| Ferramenta | Sensibilidade | Especificidade | Acurácia |
|---|---|---|---|
| CPPred | 0,98 | 1,00 | 0,990 |
| LGC | 0,89 | 1,00 | 0,945 |
| CNCI | 0,89 | 0,98 | 0,935 |

- Docker e Apptainer produziram saídas **idênticas byte a byte** (CPPred, CNCI) e rótulos idênticos (LGC).
- Execuções simultâneas da mesma imagem não interferem entre si.

## Licenças

CNCI GPL-2.0, CPAT GPL-2.0-or-later, CPC2 GPL-3.0, PLEK GPL-2.0, RNAsamba GPL-3.0; LIBSVM (dentro do
CNCI e do CPPred) BSD-3-Clause. CPPred e LGC **não declaram licença**: os arquivos originais e as
imagens são redistribuídos sem modificação apenas para reprodutibilidade, com todos os direitos
reservados aos autores; a pedido deles, passam a ser baixados da fonte no build. Ver a seção
"License" do README principal.
