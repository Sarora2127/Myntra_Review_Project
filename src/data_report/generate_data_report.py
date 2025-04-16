# src > data_report > generate_data_report.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.ml_model.train_model import train_models
import os, sys
from src.exception import CustomException

class DashboardGenerator :
    def __init__(self, data):
        self.data = data
    def display_general_info(self):
        st.header("General Information")
        # Convert 'Over_All_Rating','Price' and 'Rating' columns to numeric
        self.data['Over_All_Rating']=pd.to_numeric(self.data['Over_All_Rating'], errors = 'coerce')
        self.data['Price']=pd.to_numeric(
            self.data['Price'].apply(lambda x: x.replace("₹","")), errors = 'coerce'
        )
        self.data['Rating'] = pd.to_numeric(self.data['Rating'], errors = 'coerce')
        # Summary pie chart of average ratings by product
        product_ratings = self.data.groupby('Product Name', as_index = False)['Over_All_Rating'].mean().dropna()
        fig_pie = px.pie(product_ratings, values='Over_All_Rating', names='Product Name', title = 'Average Ratings by Product')
        st.plotly_chart(fig_pie) # PIE CHART
        # Bar chart comparing average prices of different products with different colors
        avg_prices = self.data.groupby('Product Name', as_index=False)['Price'].mean().dropna()
        fig_bar = px.bar(avg_prices, x='Product Name', y='Price',color='Product Name', title='Average Price Comparison Between Products', color_discrete_sequence = px.colors.qualitative.Bold)
        fig_bar.update_xaxes(title="Product Name")
        fig_bar.update_yaxes(title="Average Price")
        st.plotly_chart(fig_bar)
    
    '''def display_product_sections(self):
        st.header("Product Sections")
        product_names = self.data['Product Name'].unique()
        columns = st.columns(len(product_names))

        for i, product_name in enumerate(product_names):
            product_data = self.data[self.data['Product Name'] == product_name]

            with columns[i]:
                st.subheader(f'{product_name}')

                # Display price in text or markdown with emojis
                avg_price = product_data['Price'].mean()
                st.markdown(f"💰 Average Price: ₹{avg_price:.2f}")

                # Display average rating
                avg_rating = product_data['Over_All_Rating'].mean()
                st.markdown(f"⭐ Average Rating: {avg_rating:.2f}")

                # Display top positive comments with great ratings
                positive_reviews = product_data[product_data['Rating'] >= 4.5].nlargest(5, 'Rating')
                st.subheader('Positive Reviews')
                for index, row in positive_reviews.iterrows():
                    st.markdown(f"✨ Rating: {row['Rating']} - {row['Comment']}")

                # Display top negative comments with worst ratings
                negative_reviews = product_data[product_data['Rating'] <= 2].nsmallest(5, 'Rating')
                st.subheader('Negative Reviews')
                for index, row in negative_reviews.iterrows():
                    st.markdown(f"💢 Rating: {row['Rating']} - {row['Comment']}")

                # Display rating counts in different categories
                st.subheader('Rating Counts')
                rating_counts = product_data['Rating'].value_counts().sort_index(ascending=False)
                for rating, count in rating_counts.items():
                    st.write(f"🔹 Rating {rating} count: {count}")'''
    
    def display_product_sections(self):
        st.header("🛍️ Product Showcase")

        product_names = self.data['Product Name'].unique()

        for product_name in product_names:
            product_data = self.data[self.data['Product Name'] == product_name]

            # Collapsible product section
            with st.expander(f"📦 {product_name}", expanded=False):
                avg_price = product_data['Price'].mean()
                avg_rating = product_data['Over_All_Rating'].mean()

                # Card layout
                col1, col2 = st.columns([1, 3])
                with col1:
                    # You can replace with actual image if available
                    st.image("src/data_report/images-removebg-preview.png", caption="Product Image", width=100)
                with col2:
                    st.subheader(product_name)
                    st.markdown(f"💰 **Average Price:** ₹{avg_price:.2f}")
                    st.markdown(f"⭐ **Average Rating:** {avg_rating:.2f}")

                # Positive Reviews Section
                st.markdown("---")
                st.subheader("🟢 Top Positive Reviews")
                positive_reviews = product_data[product_data['Rating'] >= 4.5].nlargest(5, 'Rating')
                if not positive_reviews.empty:
                    for _, row in positive_reviews.iterrows():
                        st.markdown(f"✨ **Rating {row['Rating']}**: _{row['Comment']}_")
                else:
                    st.info("No positive reviews available.")

                # Negative Reviews Section
                st.subheader("🔴 Top Negative Reviews")
                negative_reviews = product_data[product_data['Rating'] <= 2].nsmallest(5, 'Rating')
                if not negative_reviews.empty:
                    for _, row in negative_reviews.iterrows():
                        st.markdown(f"💢 **Rating {row['Rating']}**: _{row['Comment']}_")
                else:
                    st.info("No negative reviews available.")

                # Rating Counts
                st.subheader("📊 Rating Distribution")
                rating_counts = product_data['Rating'].value_counts().sort_index(ascending=False)
                for rating, count in rating_counts.items():
                    st.markdown(f"🔹 **{rating} stars**: {count} review(s)")

                st.markdown("---")

                    
    def display_sales_prediction(self):
        st.header("📈 Popularity Score (Mini Version of Sales)")
        st.markdown("""
        💡 **Note:**  
        Popularity Score is approximated using `Rating_Count` and `Rating`, which reflects the number of users who rated the product. Predictions are made using machine learning models trained on scraped product data like price, Over-all-Rating, Positive Word Count, Negative Word Count.
        """)
        # print(self.data.Price) problem is price is not retrieved from mongo DB
        with st.spinner("Training ML models..."):
            results = train_models(self.data)
        # Collect model scores
        model_names = []
        rmse_scores = []
        r2_scores = []

        for res in results:
            model_names.append(res["name"])
            rmse_scores.append(res["rmse"])
            r2_scores.append(res["r2"])

        # --- 📊 RMSE Chart ---
        st.subheader("📊 Model Performance - RMSE")
        fig_rmse = px.bar(
            x=model_names, y=rmse_scores, labels={"x": "Model", "y": "RMSE"}, color=model_names,
            title="Root Mean Squared Error (Lower = Better)"
        )
        st.plotly_chart(fig_rmse)

        # --- 📈 R² Chart ---
        st.subheader("📈 Model Performance - R² Score")
        fig_r2 = px.bar(
            x=model_names, y=r2_scores, labels={"x": "Model", "y": "R² Score"}, color=model_names,
            title="R² Score (Closer to 1 = Better)"
        )
        st.plotly_chart(fig_r2)

        # --- 📌 Feature Importance ---
        for res in results:
            if res["feature_importance"] is not None:
                st.subheader(f"🔍 Feature Importance - {res['name']}")
                fig_feat = px.bar(
                    res["feature_importance"].nlargest(10, "Importance"),
                    x="Importance", y="Feature", orientation='h', color="Feature"
                )
                st.plotly_chart(fig_feat)

        # --- 🔮 Actual vs Predicted Chart (Only for the best model) ---
        best_model = max(results, key=lambda x: x["r2"])
        st.subheader(f"📉 Actual vs Predicted Sales using {best_model['name']}")

        # Re-train on full data for better visualization
        from src.ml_model.utils import preprocess_data
        preprocessor, X_train, X_test, y_train, y_test = preprocess_data(self.data)

        from sklearn.pipeline import Pipeline
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", best_model["model"])
        ])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        comparison_df = pd.DataFrame({
            "Actual Sales (Rating Count)": y_test,
            "Predicted Sales": y_pred
        }).reset_index(drop=True)

        fig_pred = px.line(
            comparison_df, 
            y=["Actual Sales (Rating Count)", "Predicted Sales"],
            title="Actual vs Predicted Sales",
            labels={"value": "Sales", "index": "Sample"},
            markers=True
        )
        st.plotly_chart(fig_pred)

       