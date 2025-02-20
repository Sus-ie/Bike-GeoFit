# Bike Fit & Geometry Recommendation System

## 📚 Project Overview

This project presents a **data-driven bike fitting and geometry recommendation system** designed to provide tailored bike suggestions based on user preferences and physical attributes. The system leverages:

- **Web-scraped data** from cycling geometry databases.
- Comprehensive **data cleaning** and **exploratory data analysis (EDA)** using **Python** and **Jupyter Notebooks**.
- **Interactive dashboards** built with **Tableau** to visualize key industry trends.
- A **Streamlit web application** for real-time user recommendations based on geometry data.

### 🚴 Project Highlights
- Analysis of **frame size trends**, showing a growing preference for larger frames (XL, XXL).
- Insights into **wheel size evolution** and **market segmentation**, highlighting the rise of **Gravel/CX** bikes.
- Examination of how the **pandemic influenced cycling trends**, with a surge in bike models between 2020-2022.
- Development of a **recommendation system** that matches riders with suitable bikes based on their height, inseam, and riding style.

---

## 🛠️ Technologies Used

- **Python:** Pandas, NumPy, Matplotlib, Seaborn, Scipy, sklearn
- **Web Scraping:** BeautifulSoup, requests, Selenium
- **EDA & Analysis:** Jupyter Notebooks (`EDA.ipynb`)
- **Visualization:** Tableau (`BikeFit.twb`)
- **App Development:** Streamlit
- **Deployment:** Docker (recommended), AWS/Heroku (for scalability)

---

## 💾 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/bike-fit-recommendation.git
cd bike-fit-recommendation

# Create and activate the virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

### 📊 Explore Tableau Dashboards
- Open `BikeFit.twb` in **Tableau Desktop** for insights on market trends and geometry data.

---

## 🌟 Key Insights

- **Performance Trends:** Larger frames are trending, reflecting performance-focused designs.
- **Design Preferences:** Surge in **Road** and **Gravel/CX** bike models post-2018.
- **Market Dynamics:** Brands like **Canyon** and **Nicolai** strategically lead niche categories.
- **Pandemic Influence:** The 2020-2022 period saw increased cycling interest and bike model releases.

---

## 🚀 Future Work

- **Machine Learning Integration:** Predictive analytics using **Random Forest** and **XGBoost** for enhanced recommendations.
- **Real-Time Data Integration:** API connections for live pricing and stock updates.
- **User Personalization:** Account features and feedback loops for continuous improvement.
- **Advanced Analytics:** Deep-dive into brand segmentation using clustering techniques.

---

## 🙌 Acknowledgments

Special thanks to:

- **IronHack** for the learning platform and support.
- **Isidre Munné-Bertran** and **Nicolas Mirabet** for their invaluable mentorship and guidance throughout the project.
- The **Streamlit**, **Tableau**, and **Python** communities for extensive documentation and tools.

---

## ✨ Final Note

> *"This project demonstrates how data-driven solutions can enhance user experiences by delivering tailored recommendations in the cycling industry. Here’s to smoother rides and better fits—powered by data. Happy cycling!"* 🚴‍♂️✨

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 💡 How to Contribute

1. **Fork** the repository.
2. **Create a new branch:**
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. **Commit your changes:**
   ```bash
   git commit -m "Add some feature"
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature/YourFeatureName
   ```
5. **Create a pull request.**

---

## 🔗 Links

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Tableau Public](https://public.tableau.com/)
- [Python Official](https://www.python.org/)

