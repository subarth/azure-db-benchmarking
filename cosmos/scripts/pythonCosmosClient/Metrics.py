import asyncio
import time
from datetime import datetime, timezone
import csv

REPORT_INTERVAL = 10  # seconds
CSV_FILENAME = "metrics_log.csv"
CHART_FILENAME = "metrics_chart.png"
LATENCY_CHART_FILENAME = "latency_chart.png"
EXCEL_FILENAME = "metrics_summary.xlsx"

class Metrics:
    def __init__(self, label):
        self.label = label
        self.latencies_us = []
        self.errors = 0
        self.total_ops = 0
        self.lock = asyncio.Lock()
        self.last_refresh = time.perf_counter()

    async def record(self, latency_us, success):
        async with self.lock:
            self.latencies_us.append(latency_us)
            if not success:
                self.errors += 1
            self.total_ops += 1

    async def summarize(self, label, start_time):
        async with self.lock:
            elapsed = (time.perf_counter_ns() - start_time) / 1_000_000_000
            latencies = sorted(self.latencies_us)
            max_latency = max(latencies)
            min_latency = min(latencies)
            avg_latency = sum(latencies) / len(latencies)
            total_ops = self.total_ops
            errors = self.errors
            self.latencies_us = []
            self.errors = 0
            self.total_ops = 0
            last_refresh = time.perf_counter_ns()
            self.last_refresh = last_refresh
        ops_per_sec = total_ops / elapsed if elapsed else 0
        availability = 100 * (1 - errors / total_ops) if total_ops else 0

        def percentile(p):
            if not latencies:
                return 0.0
            k = int(p * len(latencies)) - 1
            return latencies[max(0, k)]

        return {
            "operation": label,
            "ops_per_sec": ops_per_sec,
            "total_ops": total_ops,
            "max_latency": max_latency,
            "min_latency": min_latency,
            "avg_latency": avg_latency,
            "availability": availability,
            "p99": percentile(0.99),
            "p99_9": percentile(0.999),
            "p99_99": percentile(0.9999),
            "refresh_time": last_refresh,
        }

    @staticmethod
    def generate_summary_artifacts(csv_file: str):
        print("Generating summary artifacts")
        # try:
        #     df = pd.read_csv(csv_file, parse_dates=["timestamp"])
        #     df["timestamp"] = pd.to_datetime(df["timestamp"])
        #     df["timestamp"] = df["timestamp"].dt.tz_localize(None)
        #
        #     # Plot Ops/sec Chart
        #     plt.figure(figsize=(10, 6))
        #     for op in df["operation"].unique():
        #         subset = df[df["operation"] == op]
        #         plt.plot(subset["timestamp"], subset["ops_per_sec"], label=f"{op} Ops/sec")
        #     plt.title("Cosmos DB Ops/sec Over Time")
        #     plt.xlabel("Time")
        #     plt.ylabel("Ops/sec")
        #     plt.legend()
        #     plt.tight_layout()
        #     plt.savefig(CHART_FILENAME)
        #     plt.close()
        #
        #     # Plot Latency Percentiles Chart
        #     plt.figure(figsize=(10, 6))
        #     for op in df["operation"].unique():
        #         subset = df[df["operation"] == op]
        #         plt.plot(subset["timestamp"], subset["p99 (us)"], label=f"{op} P99")
        #         plt.plot(subset["timestamp"], subset["p99_9 (us)"], label=f"{op} P99.9", linestyle="--")
        #         plt.plot(subset["timestamp"], subset["p99_99 (us)"], label=f"{op} P99.99", linestyle=":")
        #     plt.title("Cosmos DB Latency Percentiles Over Time")
        #     plt.xlabel("Time")
        #     plt.ylabel("Latency (µs)")
        #     plt.legend()
        #     plt.tight_layout()
        #     plt.savefig(LATENCY_CHART_FILENAME)
        #     plt.close()
        #
        #     # Excel Summary
        #     with pd.ExcelWriter(EXCEL_FILENAME, engine="openpyxl") as writer:
        #         df.to_excel(writer, sheet_name="RawData", index=False)
        #
        #     wb = load_workbook(EXCEL_FILENAME)
        #
        #     ws_chart1 = wb.create_sheet("OpsChart")
        #     chart1 = XLImage(CHART_FILENAME)
        #     chart1.anchor = "A1"
        #     ws_chart1.add_image(chart1)
        #
        #     ws_chart2 = wb.create_sheet("LatencyChart")
        #     chart2 = XLImage(LATENCY_CHART_FILENAME)
        #     chart2.anchor = "A1"
        #     ws_chart2.add_image(chart2)
        #
        #     wb.save(EXCEL_FILENAME)
        #     print("✅ Charts saved: metrics_chart.png, latency_chart.png")
        #     print(f"✅ Excel summary saved: {EXCEL_FILENAME}")
        # except Exception as e:
        #     print(f"❌ Unexpected error: {e}")

    @staticmethod
    async def print_and_log_metrics(start_time, metric, append_logs=False):
        file_mode = "a" if append_logs else "w"
        with open(CSV_FILENAME, mode=file_mode, newline="") as f:
            try:
                writer = csv.DictWriter(f, fieldnames=[
                    "timestamp", "operation", "ops_per_sec", "ops",
                    "max_latency", "min_latency", "avg_latency",
                    "availability", "p99 (us)", "p99_9 (us)", "p99_99 (us)"
                ])
                if file_mode == "w":
                    writer.writeheader()
                while True:
                    await asyncio.sleep(REPORT_INTERVAL)
                    start_time = (await Metrics.__log_metric(start_time, writer, metric))["refresh_time"]
            except asyncio.CancelledError:
                print(f"Flushing {metric.label} metrics.")
                await Metrics.__log_metric(metric.last_refresh, writer, metric)
            finally:
                print(f"{metric.label} finished.")

    @staticmethod
    async def __log_metric(start_time, writer, metric):
        ts = datetime.now(timezone.utc).isoformat()
        summary = await metric.summarize(metric.label, start_time)
        print(f"{metric.label:<6} | "
              f"Timestamp: {ts} | "
              f"Ops/sec: {summary['ops_per_sec']:.1f} | "
              f"Total Ops: {summary['total_ops']:.1f} | "
              f"Max Latency: {summary['max_latency']:.1f} | "
              f"Min Latency: {summary['min_latency']:.1f} | "
              f"Avg Latency: {summary['avg_latency']:.1f} | "
              f"Avail: {summary['availability']:.2f}% | "
              f"P99: {summary['p99']:.0f}µs | "
              f"P99.9: {summary['p99_9']:.0f}µs | "
              f"P99.99: {summary['p99_99']:.0f}µs")
        writer.writerow({
            "timestamp": ts,
            "operation": summary["operation"],
            "ops_per_sec": summary["ops_per_sec"],
            "ops": summary["total_ops"],
            "max_latency": summary["max_latency"],
            "min_latency": summary["min_latency"],
            "avg_latency": summary["avg_latency"],
            "availability": summary["availability"],
            "p99 (us)": summary["p99"],
            "p99_9 (us)": summary["p99_9"],
            "p99_99 (us)": summary["p99_99"],
        })
        return {
            "refresh_time": summary["refresh_time"],
        }