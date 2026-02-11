# 📖 Book Recommender App Project 
[Book Recommender App] is a context-aware engine designed to solve *Choice Overload* in the reading world. While traditional platforms rely on static genres, authors etc, we match readers with the perfect book for their specific moment.

## 🛠️ Tech Stack & Tools

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat&logo=jupyter&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?logo=numpy&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/Beautiful%20Soup-Web%20Scraping-006400?style=flat&logo=python&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-Statistical%20Visualization-4C72B0?style=flat&logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557C?style=flat&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP%20Library-005500?style=flat&logo=python&logoColor=white)
![Time](https://img.shields.io/badge/Time-3776AB?style=flat&logo=python&logoColor=white)
![ML](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)
![SBERT](https://img.shields.io/badge/SBERT-Sentence--Transformers-3465A4?style=flat&logo=huggingface&logoColor=white)
![TF-DF](https://img.shields.io/badge/TF--DF-TensorFlow--Decision--Forests-FF6F00?style=flat&logo=tensorflow&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)

---

## 📚Project Background & Overview

**The Friction: Decision Paralysis**

Users often spend more time browsing than reading, and half of them do not even finish the book. This "Paradox of Choice" leads to fatigue, where the sheer volume of options prevents any decision from being made.

**The Fix: Contextual Recommendation**

We replace choice fatigue with Situational Matching. Instead of asking "What genre do you like?", we ask "What is your current moment?"


## 📊 Data Architecture

| Pillar                       | Source                                                    | Key Features / Data Points                                                                   |
| :----------------------------- | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| **Top Rated Fictions**             | Goodreads Web Scraping                               |  Title, Author, Genre, Rating, Description, Number of pages, ISBN, Language, Published Year, Book Cover Image, Link to the book    |
| **Popular Non-Fictions(Historical, Biography)**         | Open Library API                            | Title, Author, Genre, Rating, Rating counts, Description, Number of pages, ISBN, Language, Published Year, Book Cover Image, Link to the book   |                             


##  📈 Executive Summary
- **Beyond Genres**: Our EDA revealed that "Genre" is often misleading for situational needs. A dark sci-fi might be perfect for a flight (Adrenaline) but terrible for winding down (Bedtime).

- **Logical Reliability**: By choosing a deterministic weighted system over a raw ML model for the final version, we ensured the recommendations are consistent, explainable, and fast. 


## 💡Insight Deepdive 

Our EDA revealed that a reader's environment dictates their expectations:

- **Subjectivity Gap**: Emotional and Poetic books have the highest rating variance, because they are open to interpretation, they are "risky" recommendations.

- **The Non-Fiction Trap**: Real-life books show the most low-rank outliers, indicating a high volume of poorly executed biographies/histories.

- **Polarised vs. Consistent**: [Polarising] Educational, Adrenaline, Bedtime moods show wide rating swings, personal taste varies wildly here. [Consistent] Easy-read, On-the-go, Beach moods show tight rating consensus.
  

## 🎯 Future Roadmap 
[Product Evolution]

- **Hybrid Recommender**: Adding Collaborative Filtering (User-to-User logic).

- **NLP Depth**: Automating "vibe" tagging via Hugging Face.

- **Personalisation**: Adding Like/Dislike feedback and Custom Weighting settings.

[Commercial Angles]

- **Monetisation**: Moving to Freemium with social gamification and "Deep Dive" picks.

- **Omnichannel**: Expanding affiliate links (Dussmann, etc.) and In-Shop retail tools.

Presentation Slides [here]() 

