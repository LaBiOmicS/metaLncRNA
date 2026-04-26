import multiprocessing
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from ..adapters.cnci import CNCIAdapter
from ..adapters.cpat import CPATAdapter
from ..adapters.cpc2 import CPC2Adapter
from ..adapters.cppred import CPPredAdapter
from ..adapters.lgc import LGCAdapter
from ..adapters.plek import PLEKAdapter
from ..adapters.rnasamba import RNAsambaAdapter
from ..utils.logger import logger


class Dispatcher:
    """
    Orchestrates tool execution with resource management and isolation.
    """
    def __init__(
        self,
        config: Dict[str, Any],
        n_jobs: Optional[int] = None,
        use_mamba: bool = True,
        keep_intermediates: bool = False,
    ):
        self.config = config
        self.use_mamba = use_mamba
        self.keep_intermediates = keep_intermediates
        self.n_jobs = n_jobs or min(len(config), multiprocessing.cpu_count())
        self.adapters = self._init_adapters()

    def _init_adapters(self) -> Dict[str, Any]:
        adapters = {}

        def get_c(name):
            return self.config.get(name, {})

        if "rnasamba" in self.config:
            c = get_c("rnasamba")
            adapters["rnasamba"] = RNAsambaAdapter(
                weights_path=c.get("weights"),
                tool_path=c.get("path", "rnasamba"),
                env_name=c.get("env_name", "metalnc_rnasamba"),
            )
        if "cpc2" in self.config:
            c = get_c("cpc2")
            adapters["cpc2"] = CPC2Adapter(
                tool_path=c.get("path", "CPC2.py"), env_name=c.get("env_name", "metalnc_cpc2"), use_mamba=self.use_mamba
            )
        if "cpat" in self.config:
            c = get_c("cpat")
            adapters["cpat"] = CPATAdapter(
                logit_model=c.get("logit_model"),
                hexamer_table=c.get("hexamer_table"),
                tool_name=c.get("path", "cpat.py"),
                env_name=c.get("env_name", "metalnc_cpat"),
            )
        if "plek" in self.config:
            c = get_c("plek")
            adapters["plek"] = PLEKAdapter(
                tool_name=c.get("path", "PLEK.py"), env_name=c.get("env_name", "metalnc_plek")
            )

        # Internal / Legacy tools
        if "cppred" in self.config:
            c = get_c("cppred")
            adapters["cppred"] = CPPredAdapter(
                tool_name=c.get("path", "CPPred_fixed.py"), env_name=c.get("env_name", "metalnc_legacy")
            )

        if "cnci" in self.config:
            c = get_c("cnci")
            adapters["cnci"] = CNCIAdapter(
                mode=c.get("mode", "ve"),
                tool_name=c.get("path", "CNCI.py"),
                env_name=c.get("env_name", "metalnc_legacy"),
            )
        if "lgc" in self.config:
            c = get_c("lgc")
            adapters["lgc"] = LGCAdapter(
                tool_name=c.get("path", "lgc-1.0.0.py"), env_name=c.get("env_name", "metalnc_legacy")
            )

        return adapters

    def run_tool_safe(self, name, adapter, input_fasta, output_dir, log_file, intermediate_dir):
        final_out = output_dir / f"{name}_standardized.tsv"

        # CHECKPOINT
        if final_out.exists():
            logger.info(f"Checkpoint found for {name}. Skipping tool execution.")
            return name, pd.read_csv(final_out, sep="\t")

        try:
            raw_output = adapter.run(input_fasta, intermediate_dir, log_file=log_file)
            res = adapter.parse_results(raw_output)

            final_out = output_dir / f"{name}_standardized.tsv"
            res.to_csv(final_out, sep="\t", index=False)

            # Clean up raw files if not keeping intermediates
            if not self.keep_intermediates:
                if raw_output.is_file(): raw_output.unlink()
                elif raw_output.is_dir(): shutil.rmtree(raw_output)
            return name, res
        except Exception as e:
            if log_file:
                with open(log_file, "a") as f:
                    f.write(f"\nCRITICAL EXCEPTION in {name}: {str(e)}\n")
                    import traceback
                    f.write(traceback.format_exc())
            return name, e

    def run_all(self, input_fasta, output_dir, log_file=None, parallel=True):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        intermediate_dir = output_dir / "intermediates"
        intermediate_dir.mkdir(parents=True, exist_ok=True)

        results = {}
        for name, adapter in self.adapters.items():
            name, res = self.run_tool_safe(name, adapter, input_fasta, output_dir, log_file, intermediate_dir)
            if not isinstance(res, Exception): results[name] = res

        if not self.keep_intermediates and intermediate_dir.exists():
            shutil.rmtree(intermediate_dir)
        return results
