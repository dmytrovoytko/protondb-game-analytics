# ProtonDB Game Analytics data engineering project

Data Engineering project for DE ZoomCamp'26: ProtonDB reports -> (Bruin) -> DuckDB/BigQuery -> Dashboards in Streamlit

ETL workflow for 🎮 [ProtonDB Gaming reports data](https://github.com/bdefore/protondb-data)

![Data Engineering ProtonDB Game Analytics](/screenshots/streamlit3.png)

Project can be tested and deployed in **GitHub CodeSpaces** (the easiest option, and free), cloud virtual machine (AWS, Azure, GCP), or just locally.
For the GitHub CodeSpace option you don't need to use anything extra at all - just your favorite web browser + GitHub account is totally enough.

## Problem statement

If you feel deeply unsatisfied by Windows unreliable behavior/performace, or just curious about switching to Linux, but your desire to play games is stopping you, you might need Linux Gaming Analytics. With ProtonDB.com you can find out what games reliably play on Linux, which distros and hardware could be the best choice for your switch. Gamers from around the world submit reports on which games play well, and which don't even install.
But if you don't want to dig into those reports, you probably just need a few dashboards that this project provides to make your decision quickly.

## 🎯 Goals

This is my Data Engineering project in [DE ZoomCamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)'2025.

**The main goal** is straight-forward: build an end-to-end **Extract - Load - Transform** data pipeline, then **visualize** some insights.  
- choose an interesting dataset
- process (extract, transform, load) data
- deploy orchestration tool to manage pipeline
- build a dashboard to visualize the data

🕵️ Questions that I want to investigate during this project:

- What Linux distros are popular among gamers?
- What hardware would work well (or be enough) for Linux gaming?
- Which popular games work well, and which don't on Linux?

## :toolbox: Tech stack

- Python 3.12/3.13
- **Docker** and docker-compose for containerization
- [Terraform for infrastructure (in progress)]
- **Bruin** as pipeline tool
- **DuckDB** (MotherDuck) for data warehouse [or/and **BigQuery** (in progress)]
- [optional (in progress)] Google Cloud Storage
- **Pandas** for data processing
- Plotly and Streamlit charts for data visualization
- **Streamlit** for dashboards

## 🚀 Instructions to reproduce

- [Setup environment](#hammer_and_wrench-setup-environment)
- [Run workflow](#arrow_forward-run-workflow)
- [Dashboard](#mag_right-dashboard)

### :hammer_and_wrench: Setup environment



### 📊📈 Dashboards

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard1.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard2.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard3.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard4.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard5.png)

## Support

🙏 Thank you for your attention and time!

- If you experience any issue while following this instruction (or something left unclear), please add it to [Issues](/issues), I'll be glad to help/fix. And your feedback, questions & suggestions are welcome as well!
- Feel free to fork and submit pull requests.

If you find this project helpful, please ⭐️star⭐️ my repo 
https://github.com/dmytrovoytko/protondb-game-analytics to help other people discover it 🙏

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko