# tests/test_performance_lighthouse
import allure
import pytest
import pytest_check as check
from base.base_test import BaseTest
from base.lighthouse_runner import LighthouseRunner 
from utils.config_reader import ConfigReader


class TestPerformanceLighthouse(BaseTest):
    cfg = ConfigReader.load_config("config_mobile.json")

    #️ Gom pages thành structure chuẩn
    BRANDS = [
        ("paved", cfg["PAVED_PAGES"]),
        ("gsa",   cfg.get("GSA_PAGES", [])),
    ]
    # Add mode param: desktop + mobile
    MODES = ["mobile"]
    RUNS_PER_PAGE = 3 # ==> run 3 times

    # ======================================================
    # MAIN TEST
    # ======================================================
    @pytest.mark.parametrize("brand,pages", BRANDS)
    @pytest.mark.parametrize("mode", MODES)
    def test_performance_lighthouse(self, brand, pages, mode):

        for url, page_name in pages:

            run_results = []

            # --------------------------
            # Run Lighthouse n times
            # --------------------------
            for i in range(1, self.RUNS_PER_PAGE + 1):
                report_dir = f"reports_{mode}/{brand}/run_{i}"
                json_path, html_path = LighthouseRunner.run(url, mode, report_dir)

                run_results.append({
                    "run": i,
                    "json": json_path,
                    "html": html_path,
                    "scores": LighthouseRunner.parse_scores(json_path)
                })

            # Attach all run HTML
            self.attach_all_runs(brand, mode, page_name, run_results)

            # Detect abnormal drops
            mean_perf, abnormal_runs = self.detect_abnormal(run_results)
            self.attach_abnormal_warning(brand, page_name, mean_perf, abnormal_runs)

            # Summary table
            self.attach_summary_table(brand, page_name, mode, run_results, abnormal_runs)

            # Evaluate pass/fail on last run
            final_scores = run_results[-1]["scores"]
            threshold = self.cfg["THRESHOLDS"]["PERFORMANCE"] * 100
            is_pass = final_scores["Performance"] >= threshold

            # Save all 3 runs
            self.save_all_runs(is_pass, mode, brand, page_name, run_results)

            # Soft assertion—doesn't stop next tests
            check.is_true(
                is_pass,
                f"❌ {brand.upper()} {page_name} FAILED — "
                f"Performance {final_scores['Performance']} < {threshold}"
            )