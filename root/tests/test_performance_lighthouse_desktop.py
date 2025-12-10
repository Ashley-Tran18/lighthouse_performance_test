# tests/test_performance_lighthouse
import allure
import pytest
import pytest_check as check
from base.base_test import BaseTest
from base.lighthouse_runner import LighthouseRunner 
from utils.config_reader import ConfigReader


class TestPerformanceLighthouse(BaseTest):
    cfg = ConfigReader.load_config("config_desktop.json")

    #️ Gom pages thành structure chuẩn
    BRANDS = [
        ("paved", cfg["PAVED_PAGES"]),
        ("gsa",   cfg.get("GSA_PAGES", [])),
    ]
    # Add mode param: desktop + mobile
    MODES = ["desktop"]
    RUNS_PER_PAGE = 5 # ==> run 3 times

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


# @pytest.mark.parametrize("brand,pages", BRANDS)
# @pytest.mark.parametrize("mode", MODES)

# def test_performance_lighthouse(brand, pages, mode):
    
#     for url, page_name in pages:
        
#         report_dir = f"reports_{mode}/{brand}"
#         base_run_dir = f"reports_temp/{mode}/{brand}/{page_name}"
#         run_results = [] 

#         # ===========================================
#         # 🔄 Run 3 times
#         # ===========================================
#         for run_idx in range(1, RUNS_PER_PAGE + 1):
            
#             run_dir = f"{base_run_dir}/run_{run_idx}"
           
#             json_path, html_path = LighthouseRunner.run(
#                 url, 
#                 mode=mode, 
#                 report_dir=f"{report_dir}/run_{run_idx}"
#             )
#                # Parse score
#             scores = LighthouseRunner.parse_scores(json_path)

#             # Save every run
#             run_results.append({
#                 "run": run_idx,
#                 "json": json_path,
#                 "html": html_path,
#                 "scores": scores
#             })
#         # ===========================================
#         # 🔗 ATTACH ALL RUNS TO ALLURE
#         # ===========================================
#         for r in run_results:
#             with open(r["html"], "rb") as f:
#                 allure.attach(
#                     f.read(),
#                     f"[RUN {r['run']}] {brand.upper()} {mode.capitalize()} - {page_name}",
#                     allure.attachment_type.HTML
#                 )

#         # ===========================================
#         # 📉 DETECT ABNORMAL PERFORMANCE DROP >20%
#         # ===========================================
#         perf_values = [r["scores"]["Performance"] for r in run_results]
#         mean_perf = sum(perf_values) / len(perf_values)

#         abnormal_runs = []
#         for r in run_results:
#             perf = r["scores"]["Performance"]
#             if abs(perf - mean_perf) / mean_perf >= 0.20:   # Drop >= 20%
#                 abnormal_runs.append(r)

#         # Attach warning if any abnormal run
#         if abnormal_runs:
#             warn_html = "<h3 style='color:red;'>⚠️ Abnormal Performance Detected</h3>"
#             warn_html += f"<p>Mean Performance: <b>{mean_perf:.2f}</b></p>"
#             warn_html += "<ul>"
#             for r in abnormal_runs:
#                 warn_html += f"<li>Run {r['run']} → {r['scores']['Performance']}</li>"
#             warn_html += "</ul>"

#             allure.attach(
#                 warn_html,
#                 f"⚠️ WARNING — Abnormal Drop Detected ({brand} - {page_name})",
#                 allure.attachment_type.HTML
#             )

#         # ===========================================
#         # 📊 SUMMARY TABLE FOR ALL RUNS
#         # ===========================================
#         table_html = """
#         <h3>Summary of 3 Lighthouse Runs</h3>
#         <table border='1' style='border-collapse:collapse;'>
#         <tr>
#             <th>Run</th>
#             <th>Performance</th>
#             <th>Accessibility</th>
#             <th>BestPractices</th>
#             <th>SEO</th>
#         </tr>
#         """

#         for r in run_results:
#             s = r["scores"]
            
#             # Highlight abnormal run
#             highlight = ""
#             if r in abnormal_runs:
#                 highlight = " style='background-color:#ffcccc; font-weight:bold;'"

#             table_html += f"""
#             <tr{highlight}>
#                 <td>{r['run']}</td>
#                 <td>{s['Performance']}</td>
#                 <td>{s['Accessibility']}</td>
#                 <td>{s['BestPractices']}</td>
#                 <td>{s['SEO']}</td>
#             </tr>
#             """

#         table_html += "</table>"

#         allure.attach(
#             table_html,
#             f"Summary Table - {brand.upper()} {page_name} [{mode}]",
#             allure.attachment_type.HTML
#         )

#         # =======================================================
#         # ✔️ ASSERTION — TÁCH PASS / FAIL
#         # =======================================================

#         last_run = run_results[-1]
#         final_scores = last_run["scores"]
#         threshold = cfg["THRESHOLDS"]["PERFORMANCE"] * 100
#         is_pass = final_scores["Performance"]>= threshold

#         # ----------------------------
#         # 📁 SAVE FINAL BEST REPORT
#         # ----------------------------
#         target_root = "reports_passed" if is_pass else "reports_failed"
#         final_target_dir = f"{target_root}/{mode}/{brand}/{page_name}"

#         # TẠO FOLDER TRƯỚC KHI COPY
#         Path(final_target_dir).mkdir(parents=True, exist_ok=True)

#         # =======================================================
#         # 📁 COPY: LƯU CẢ 3 RUN 
#         # =======================================================
#         for r in run_results:
#             shutil.copy(r["json"], f"{final_target_dir}/run_{r['run']}.json")
#             shutil.copy(r["html"], f"{final_target_dir}/run_{r['run']}.html")


#         # ASSERT but không stop test
#         check.is_true(
#             is_pass,
#             f"❌ {brand.upper()} {page_name} [{mode}] FAILED — "
#             f"Performance {final_scores['Performance']} < Threshold {threshold}"
#         )



     