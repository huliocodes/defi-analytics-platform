from flows import defi_analytics_flow


if __name__ == "__main__":
    defi_analytics_flow.serve(
        name="hourly-defi-analytics",
        cron="0 * * * *",
    )