import streamlit as st

def main():
    st.sidebar.image("img/logo.jpg", width=50)

    pg = st.navigation({"": [st.Page("Pages/Home_page.py", title="Home Page")],
                        "Explore End Points":
                            [st.Page("Pages/OffBallRuns_page.py", title="Off-Ball Runs"),
                             st.Page("Pages/Physical_page.py", title="Physical")
                             ],
                        "Reports":
                            [st.Page("Pages/Scouting_report.py", title="Winger scouting")
                             ]
                        })
    pg.run()

if __name__ == "__main__":
    main()