# ProtonDB Game Analytics data engineering project

Data Engineering project for DE ZoomCamp'26: ProtonDB reports -> (Bruin) -> DuckDB/BigQuery -> Dashboards in Streamlit

ETL workflow for 🎮 [ProtonDB Gaming reports data](https://github.com/bdefore/protondb-data)

![Data Engineering ProtonDB Game Analytics](/screenshots/streamlit3.png)

Project can be tested and deployed in **GitHub CodeSpaces** (the easiest option, and free), cloud virtual machine (AWS, Azure, GCP), or just locally.
For the GitHub CodeSpace option you don't need to use anything extra at all - just your favorite web browser + GitHub account is totally enough.

## Problem statement

If you feel deeply unsatisfied by Windows unreliable behavior/performace, or just curious about switching to Linux, but your desire to play games is stopping you, you might need Linux Gaming Analytics. With ProtonDB.com you can find out what games reliably play on Linux, which distros and hardware could be the best choice for your switch. Gamers from around the world submit reports on which games play well, and which don't even install.
But if you don't want to dig into those reports, you probably just need a few dashboards that this project provides to make your decision quickly.

Please take into account, gaming reports are just a part of total Linux usage - from volunteers who reported about their experience. So it's just a glimps of big picture, definitely with realistic corellation.

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
- [Dashboard](#-dashboards)

### :hammer_and_wrench: Setup environment

1. **Fork this repo on GitHub**. Or use `git clone https://github.com/dmytrovoytko/protondb-game-analytics.git` command to clone it locally, then `protondb-game-analytics`.
2. Create GitHub CodeSpace from the repo. You need to choose 4-core machine with 16Gb RAM.
![Create CodeSpace](/screenshots/codespace1.png)

3. **Start CodeSpace**
4. The app works in docker container, **you don't need to install packages locally to test it**.
5. Only if you want to develop the project locally, you can run `uv sync` in `pipeline` directory (project tested on python 3.12/3.13).
6. You need to copy/rename `.env.local` to `.env` and edit setting according to your environment. Run `cp .env.local .env` then edit `.env` file. Remember to never commit files containing credentials or any other sensitive information.

(in progress)
7. If you want and can use BigQuery you need to save GCP credentials to the file `gcp-credentials.json` (recommended) and then set GOOGLE_APPLICATION_CREDENTIALS in `.env` file. Then edit GCP_PROJECT_NAME, BQ_DATASET, GCS_BUCKET (optional). You also need to set proper access for the service account to access BigQuery (see the next part of description). 
8. If you want to use Terraform, set `USE_TERRAFORM=true` in `.env` file.

9. If you don't want to/can't use BigQuery, the default settings will activate alternative warehouse - DuckDb database (you can also create/use free! [MotherDuck](https://motherduck.com/) account to use cloud data warehouse).

### :arrow_forward: Run workflow

1. **Run `bash deploy.sh` to start app Docker container**. Building container takes some time. When new log messages will stop appearing, you can press enter to return to a command line (service will keep running in background).

![Bruin pipeline start](/screenshots/bruin1.png)

When you see these messages the app is ready!

![Bruin pipeline finish](/screenshots/bruin4.png)

You can scroll up to see previous messages with the steps of the workflow.

2. Workflow commands are located in `start_app.sh` 
- [it starts `terraform-setup.sh` script] (in progress)
- then installs Bruin, UV, Streamlit. 
- then starts Bruin pipeline `bruin run pipeline.yml`
- finally executes `uv run streamlit run app.py` to start dashboard app

3. Pipeline includes 3 key tasks (download dataset & unpack, extract & transform data, load data to warehouse). Pipeline files are located in `pipeline/assets` folder.

4. Dashboard app is based on Streamlit and located in `app.py`


### 📊📈 Dashboards

If you run docker container locally you can click the link `Local URL: http://localhost:8501` to open the app dashboard.

If you run container in CodeSpace it will pop-up the notification that `Your application running on port 8501 is available.` - click `Open in Browser`. 

![Streamlit app popup](/screenshots/streamlit1.png)

💡 In case you accidentally close that pop-up or dashboard page and you need it again, you can always open that page from `Ports` tab (click that little 'globe' icon over a link):

![Streamlit app ports](/screenshots/streamlit2.png)

When you open the app it shows the dialog, where you can choose a period to analize and Linux distros to compare/visualize:

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard1.png)

Check out other dashboards:

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard1.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard2.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard3.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard4.png)

![Data Engineering ProtonDB Game Analytics](/visuals/dashboard5.png)

### :stop_sign: Stop all containers

Run `docker compose down` in command line to stop the running container.

Don't forget to remove downloaded images if you experimented with project locally! Use `docker images` to list all images and then `docker image rm ...` to remove those you don't need anymore.

[And of course don't forget to destroy resources in Google Cloud/BigQuery!]


## 🔜 Next steps

I personally switched to Linux many years ago, and really happy about that. It's interesting to observe how it becomes more and more popular, including gamers as active users. Playing games on Linux becomes much easier each year - you can see positive trends on dashboard 3.

I plan to finish part of the pipeline to load data to BigQuery and Terraform scripts to allocate/destroy related infrastructure (BQ dataset and Storage bucket).

Some more insightful vizualizations coming soon also. What do you want to know about Linux Gaming?

Stay tuned!

## Support

🙏 Thank you for your attention and time!

- If you experience any issue while following this instruction (or something left unclear), please add it to [Issues](/issues), I'll be glad to help/fix. And your feedback, questions & suggestions are welcome as well!
- Feel free to fork and submit pull requests.

If you find this project helpful, please ⭐️star⭐️ my repo 
https://github.com/dmytrovoytko/protondb-game-analytics to help other people discover it 🙏

Made with ❤️ in Ukraine 🇺🇦 Dmytro Voytko