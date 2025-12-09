
import allure
from utils.config_reader import ConfigReader
from pathlib import Path
import shutil

class BaseTest:
    # ------------------------------------------------------
    # Load thresholds
    # ------------------------------------------------------
    def load_thresholds(self, config_name):
        cfg = ConfigReader.load_config(config_name)
        t = cfg["THRESHOLDS"]

        return (
            t["PERFORMANCE"] * 100,
            t["ACCESSIBILITY"] * 100,
            t["BEST_PRACTICES"] * 100,
            t["SEO"] * 100,
        )

    # ------------------------------------------------------
    # Assert scores
    # ------------------------------------------------------
    def assert_scores(self, scores, config_name):
        perf, acc, best, seo = self.load_thresholds(config_name)

        failures = []

        if scores["Performance"] < perf:
            failures.append(f"Performance {scores['Performance']:.1f}% < {perf}%")
        if scores["Accessibility"] < acc:
            failures.append(f"Accessibility {scores['Accessibility']:.1f}% < {acc}%")
        if scores["Best Practices"] < best:
            failures.append(f"Best Practices {scores['Best Practices']:.1f}% < {best}%")
        if scores["SEO"] < seo:
            failures.append(f"SEO {scores['SEO']:.1f}% < {seo}%")

        if failures:
            allure.dynamic.severity(allure.severity_level.CRITICAL)
            raise AssertionError("\n".join(failures))
        else:
            allure.dynamic.severity(allure.severity_level.NORMAL)

    # ------------------------------------------------------
    # Helper: attach all HTML reports
    # ------------------------------------------------------
    def attach_all_runs(self, brand, mode, page_name, run_results):
        for r in run_results:
            with open(r["html"], "rb") as f:
                allure.attach(
                    f.read(),
                    f"[RUN {r['run']}] {brand.upper()} {mode.capitalize()} - {page_name}",
                    allure.attachment_type.HTML
                )

    # ------------------------------------------------------
    # Helper: detect abnormal drop >20%
    # ------------------------------------------------------
    def detect_abnormal(self, run_results):
        perf_values = [r["scores"]["Performance"] for r in run_results]
        mean_perf = sum(perf_values) / len(perf_values)

        abnormal = [
            r for r in run_results
            if abs(r["scores"]["Performance"] - mean_perf) / mean_perf >= 0.20
        ]

        return mean_perf, abnormal

    # ------------------------------------------------------
    # Helper: attach abnormal warning
    # ------------------------------------------------------
    def attach_abnormal_warning(self, brand, page_name, mean_perf, abnormal_runs):
        if not abnormal_runs:
            return

        warn_html = f"""
        <h3 style='color:red;'>⚠️ Abnormal Performance Detected</h3>
        <p>Mean Performance: <b>{mean_perf:.2f}</b></p>
        <ul>
            {''.join([f"<li>Run {r['run']} → {r['scores']['Performance']}</li>" for r in abnormal_runs])}
        </ul>
        """

        allure.attach(
            warn_html,
            f"⚠️ WARNING — Abnormal Drop ({brand} - {page_name})",
            allure.attachment_type.HTML
        )

    # ------------------------------------------------------
    # Helper: summary table
    # ------------------------------------------------------
    def attach_summary_table(self, brand, page_name, mode, run_results, abnormal_runs):
        rows = ""
        for r in run_results:
            s = r["scores"]
            highlight = " style='background-color:#ffcccc; font-weight:bold;'" if r in abnormal_runs else ""
            rows += f"""
            <tr{highlight}>
                <td>{r['run']}</td>
                <td>{s['Performance']}</td>
                <td>{s['Accessibility']}</td>
                <td>{s['BestPractices']}</td>
                <td>{s['SEO']}</td>
            </tr>"""

        table = f"""
        <h3>Summary of Lighthouse Runs</h3>
        <table border='1' style='border-collapse:collapse;'>
            <tr>
                <th>Run</th>
                <th>Performance</th>
                <th>Accessibility</th>
                <th>BestPractices</th>
                <th>SEO</th>
            </tr>
            {rows}
        </table>
        """

        allure.attach(
            table,
            f"Summary Table - {brand.upper()} {page_name} [{mode}]",
            allure.attachment_type.HTML
        )

    # ------------------------------------------------------
    # Helper: save all run reports
    # ------------------------------------------------------
    def save_all_runs(self, is_pass, mode, brand, page_name, run_results):
        target_root = "reports_passed" if is_pass else "reports_failed"
        final_target = f"{target_root}/{mode}/{brand}/{page_name}"
        Path(final_target).mkdir(parents=True, exist_ok=True)

        for r in run_results:
            shutil.copy(r["json"], f"{final_target}/run_{r['run']}.json")
            shutil.copy(r["html"], f"{final_target}/run_{r['run']}.html")
