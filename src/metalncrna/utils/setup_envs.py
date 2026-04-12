import subprocess
import os
import json
from pathlib import Path

ENVS = {
    "rnasamba": ["mamba", "create", "-y", "-n", "metalnc_rnasamba", "-c", "conda-forge", "-c", "bioconda", "rnasamba"],
    "cpc2": ["mamba", "create", "-y", "-n", "metalnc_cpc2", "-c", "conda-forge", "-c", "bioconda", "cpc2", "python=2.7"],
    "cpat": ["mamba", "create", "-y", "-n", "metalnc_cpat", "-c", "conda-forge", "-c", "bioconda", "CPAT"],
    "plek": ["mamba", "create", "-y", "-n", "metalnc_plek", "-c", "conda-forge", "-c", "bioconda", "plek", "python=2.7", "libsvm"],
    "legacy": ["mamba", "create", "-y", "-n", "metalnc_legacy", "-c", "conda-forge", "-c", "bioconda", "python=2.7", "biopython", "scikit-learn=0.20", "numpy", "pandas", "libsvm"]
}

def get_env_path(env_name):
    try:
        result = subprocess.run(["mamba", "env", "list", "--json"], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for env_path in data.get("envs", []):
            if Path(env_path).name == env_name:
                return Path(env_path)
    except: return None
    return None

def patch_cpc2():
    prefix = get_env_path("metalnc_cpc2")
    if not prefix: return
    cpc2_script = prefix / "bin" / "CPC2.py"
    if not cpc2_script.exists(): return
    print("[*] Applying robust portability patch to CPC2...")
    data_dir = prefix / "data"
    if not (data_dir / "cpc2.model").exists():
        data_dir = prefix / "share" / "cpc2" / "data"
    with open(cpc2_script, "r") as f:
        lines = f.readlines()
    new_lines = []
    skip = False
    for line in lines:
        if 'script_dir,filename = os.path.split(os.path.abspath(sys.argv[0]))' in line:
            new_lines.append(line)
            new_lines.append(f'        data_dir = "{data_dir}/"\n')
            new_lines.append(f'        app_svm_scale = "svm-scale"\n')
            new_lines.append(f'        app_svm_predict = "svm-predict"\n')
            skip = True
            continue
        if skip and ('os.system(\'test -x\'' in line or 'app_svm_scale = ' in line or 'app_svm_predict = ' in line or 'data_dir = ' in line):
            continue
        if skip and 'cmd = app_svm_scale' in line:
            skip = False
        if "out_file = open(outfile + '.txt','w')" in line:
            new_lines.append("        out_file = open(outfile + '.final','w')\n")
            continue
        if "os.system('rm -f ' + outfile + '.tmp.1 ' + outfile + '.tmp.2 ' + outfile + '.tmp.out ' + outfile)" in line:
            new_lines.append("                os.system('rm -f ' + outfile + '.tmp.1 ' + outfile + '.tmp.2 ' + outfile + '.tmp.out')\n")
            new_lines.append("                os.system('mv ' + outfile + '.final ' + outfile)\n")
            continue
        if not skip:
            new_lines.append(line)
    with open(cpc2_script, "w") as f:
        f.writelines(new_lines)
    print("[+] CPC2 patched.")

def patch_plek():
    prefix = get_env_path("metalnc_plek")
    if not prefix: return
    plek_train = prefix / "bin" / "PLEKModelling.py"
    if not plek_train.exists(): return
    print("[*] Patching PLEK training module for Python 2.7 compatibility...")
    with open(plek_train, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if "import os, sys, traceback, getpass, time, re, subprocess" in line:
            new_lines.append(line)
            new_lines.append("import commands # Added for getstatusoutput compatibility\n")
            new_lines.append("subprocess.getstatusoutput = commands.getstatusoutput # Patch subprocess\n")
        elif "self.svmtrain_pathname = os.path.join(dirname, './svm-train')" in line:
            new_lines.append("                self.svmtrain_pathname = 'svm-train'\n")
        elif "self.svmpredict_pathname = os.path.join(dirname, './svm-predict')" in line:
            new_lines.append("                self.svmpredict_pathname = 'svm-predict'\n")
        elif "self.svmscale_pathname = os.path.join(dirname, './svm-scale')" in line:
            new_lines.append("                self.svmscale_pathname = 'svm-scale'\n")
        else:
            new_lines.append(line)
            
    with open(plek_train, "w") as f:
        f.writelines(new_lines)
    print("[+] PLEK patched.")

def create_environments(tools=None):
    tools_to_install = tools if tools else list(ENVS.keys())
    legacy_list = ["cppred", "cnci", "lgc"]
    
    envs_needed = set()
    for t in tools_to_install:
        if t in ENVS: envs_needed.add(t)
        elif t in legacy_list: envs_needed.add("legacy")
    
    for env in envs_needed:
        print(f"[*] Setting up environment: {env}...")
        subprocess.run(ENVS[env], check=True)
        if env == "cpc2": patch_cpc2()
        if env == "plek": patch_plek()
