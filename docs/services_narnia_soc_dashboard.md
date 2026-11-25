# Services Narnia | SOC Command Centre

Interactive Splunk Dashboard Studio dashboard for the synthetic 300-event Trellix Wise investigation dataset. It uses live SPL searches on the lab index; it does not contact Wise or require any tokens, app installation or administrator credentials beyond the permissions needed to create dashboards and search the index.

## Install in Splunk Web (Enterprise 10.6)

1. [Open the dashboard JSON](../dashboards/services_narnia_soc_command_centre.json) and use **Raw** or **Copy raw file** to copy the entire JSON definition. Alternatively download it with the command below.
2. Open Splunk Web, go to **Search & Reporting → Dashboards → Create New Dashboard**.
3. Set the title to **Services Narnia | SOC Command Centre**, choose **Dashboard Studio**, and select **Absolute** layout. Create the dashboard.
4. In edit mode, open the source code editor (the source/code icon). Replace the complete generated JSON with the downloaded JSON. Do not paste it into the SPL search bar.
5. Save the source and the dashboard. Use the dark theme if available for the intended presentation.
6. Leave Endpoint and Event severity set to All; use Last 24 hours or select a time range covering the dataset. If the dataset is older, choose All time. Set the dashboard's permissions to private or share only with authorised lab users.

On macOS/Linux, download the JSON file. The optional `pbcopy` command works **only in a local macOS terminal**, not on Debian/Ubuntu or in an SSH session to Linux:

```bash
curl -fsSL -o services_narnia_soc_command_centre.json https://raw.githubusercontent.com/AnamulPalash/trxwise/main/dashboards/services_narnia_soc_command_centre.json
# macOS only:
pbcopy < services_narnia_soc_command_centre.json
```

On Debian/Ubuntu/Linux, run only the `curl` download command above. To copy the JSON without installing clipboard utilities, open the [raw JSON](https://raw.githubusercontent.com/AnamulPalash/trxwise/main/dashboards/services_narnia_soc_command_centre.json) in your browser or use GitHub's **Copy raw file** button. Paste the complete JSON into the Dashboard Studio source editor. A remote SSH terminal does not normally share the local desktop clipboard.

On Windows PowerShell:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/AnamulPalash/trxwise/main/dashboards/services_narnia_soc_command_centre.json' -OutFile 'services_narnia_soc_command_centre.json'
Get-Content -Raw 'services_narnia_soc_command_centre.json' | Set-Clipboard
```

## Data and filters

- Index: `wise_data`; dataset ID: `SN-INV-2026-1125`.
- Default time range: last 24 hours. Endpoint and event-severity dropdowns apply to every panel.
- The searches extract JSON fields from the event, including the original endpoint rather than Splunk's upload host metadata. Repeated imports are deduplicated by `event_id` within the selected scope.
- If the data is in a different index, replace `index=wise_data` in both base searches in the JSON definition.
- The two base searches feed 12 visualisations through chained SPL searches. The dashboard has no periodic refresh configured. Refresh manually as needed.

## Expected initial results

With all filters open and the complete dataset in the selected time range:

| Metric | Expected |
| --- | ---: |
| Unique events | 300 |
| Products | 10 |
| Designated alerts | 3 |
| High-severity designated alerts | 2 |
| High-severity events (including context) | 7 |
| Background activity | 264 |
| Correlated case events | 36 |

The alert table should contain SN-ALERT-1125-A, B and C; the timeline includes 12 records for each of endpoints SN-WS-41, SN-WS-42 and SN-WS-43.

## Validate the data

```spl
index=wise_data earliest=0
| spath
| search dataset_id="SN-INV-2026-1125"
| dedup event_id
| stats count as Events dc(product) as Products count(eval(lower(tostring(is_alert))="true" OR event_type="alert")) as Alerts
```

Expected: 300, 10, 3.

If panels are empty, widen the time range, check the index and permissions, and run the query above in Search & Reporting. If the dataset has not been imported, follow the [timestamp refresh and Splunk import instructions in the repository README](../README.md#new-300-event-wise-investigation-agent-validation-dataset). Do not reimport just to install the dashboard.

## What the dashboard does not show

All records are fictional training telemetry. Source severity, technique tags and designated alerts are not live Wise verdicts, actual attacks or proof of real control enforcement. Wise investigation statuses and reports are not collected by this dashboard. A separate Wise monitoring view would require a supported integration or API export and a defined Splunk index/schema.

The dashboard JSON was checked for valid JSON, panel layout bounds and data source references, and the expected totals were verified against the published dataset. It has not been rendered or executed in your Splunk installation; verify it in Dashboard Studio after importing.

Reference: [Splunk Enterprise 10.6 Dashboard Studio](https://help.splunk.com/en/splunk-enterprise/create-dashboards-and-reports/dashboard-studio/10.6/introduction-to-splunk-dashboard-studio/what-is-splunk-dashboard-studio).
