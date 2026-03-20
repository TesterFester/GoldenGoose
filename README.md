# SPX Execution Dashboard — Streamlit Repo Package

This package is GitHub/Streamlit-ready.

## Files you should push to GitHub

Required for Streamlit deployment:
- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `data/spx_execution_report.json`

Included for other uses:
- `SPX_Gamma_Dashboard_Colab.ipynb`
- `spx_model_data_dictionary_v12_24.xlsx`
- `spx_model_data_dictionary_v12_24.json`
- prior versioned dictionary artifacts from the notebook package

## Recommended repo structure

```text
your-repo/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── data/
│   └── spx_execution_report.json
├── SPX_Gamma_Dashboard_Colab.ipynb
└── spx_model_data_dictionary_v12_24.xlsx
```

## Streamlit deployment steps

1. Create a GitHub repo and upload the files above.
2. In Streamlit Community Cloud, connect the repo.
3. Set the app entry point to `app.py`.
4. Deploy.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The app visualizes the JSON output from the notebook’s final report cell.
- Upload a newer `spx_execution_report.json` through the sidebar, or overwrite `data/spx_execution_report.json`.
- This package still includes the notebook and data dictionaries for audit/documentation use.
