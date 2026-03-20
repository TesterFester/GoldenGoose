# SPX Live Execution Dashboard — Streamlit Package v12.27

This package includes a live Streamlit app that runs the SPX model directly against Polygon.

## Files to push to GitHub

Required:
- `app.py`
- `spx_engine.py`
- `requirements.txt`
- `.streamlit/config.toml`

Recommended:
- `.streamlit/secrets.toml.example`
- `data/spx_execution_report.json` (sample fallback data)
- `SPX_Gamma_Dashboard_Colab.ipynb`
- `spx_model_data_dictionary_v12_27.xlsx`
- `spx_model_data_dictionary_v12_27.json`

## Streamlit secrets

In Streamlit Community Cloud, set:

```toml
POLYGON_API_KEY = "your_polygon_api_key_here"
```

## Auto-refresh schedule

New York time:
- 9:30–10:30 AM: every 30 seconds
- 10:30 AM–3:30 PM: every 60 seconds
- 3:30–4:00 PM: every 30 seconds
- outside market hours: off

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The live app regenerates `run_date_time` on each model run.
- If live execution fails or no API key is provided, the app falls back to `data/spx_execution_report.json`.
- The notebook remains included for audit/debug use.
