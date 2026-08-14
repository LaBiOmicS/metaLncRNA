load("/home/menegidio/.metalncrna/data/cpat/Human_logitModel.RData")
test <- read.table(file="/media/menegidio/Storage/Trabalho/UMC/LaBiOmics/Bioinformatics/Bioinfo/lncRNA/at/tests/test_output/ValidationRun/intermediates/cpat_raw.txt.ORF_info.tsv",sep="\t",header=T)
test$Coding_prob <- predict(mylogit,newdata=test,type="response")
write.table(test, file="/media/menegidio/Storage/Trabalho/UMC/LaBiOmics/Bioinformatics/Bioinfo/lncRNA/at/tests/test_output/ValidationRun/intermediates/cpat_raw.txt.ORF_prob.tsv", quote=F, sep="\t",row.names=FALSE, col.names=TRUE)
