# SocialFlow - Social Media Scheduler

A premium-designed web application to manage and schedule posts for multiple social media platforms. Built with Flask and modern CSS.

## Features

-   **User Authentication**: Secure Login/Register with Email Verification (Simulated).
-   **Dashboard**:
    -   View post statistics.
    -   Connect social media accounts (Twitter, Facebook, LinkedIn - Mock Integration).
    -   Manage scheduled and published posts.
-   **Post Management**:
    -   Create text posts.
    -   **Media Support**: Upload Images and Videos with instant preview.
    -   **Scheduling**: Post immediately or schedule for a future date/time.
    -   **Cancel**: Ability to cancel scheduled posts before they go live.
-   **Background Automation**: Integrated `APScheduler` runs background jobs to automatically "publish" scheduled posts when they are due.
-   **Premium UI**: Glassmorphism design with responsive layout and smooth animations.

## Tech Stack

-   **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-APScheduler.
-   **Database**: SQLite.
-   **Frontend**: HTML5, CSS3 (Vanilla + Google Fonts), JavaScript.

## Setup & Installation

1.  **Clone the repository** (or ensure you are in the project folder):
    ```bash
    cd social_media
    ```

2.  **Install Dependencies**:
    ```bash
    pip install flask flask-sqlalchemy flask-login flask-apscheduler
    ```

3.  **Run the Application**:
    ```bash
    python3 app.py
    ```

4.  **Access the App**:
    Open your browser and visit: `http://127.0.0.1:8000`

## Usage Guide

1.  **Register**: Create a new account.
2.  **Verify Email**: Check your terminal console for the simulated verification link. Click it to activate your account.
3.  **Connect Accounts**: On the dashboard sidebar, click to connect a social account (e.g., Twitter). Enter your handle (e.g., `rafi_twitter`) to link it.
4.  **Create Post**:
    -   Type your content.
    -   Drag & Drop or select an Image/Video (Preview will appear).
    -   Choose "Post Now" or "Schedule for Later".
5.  **Manage**: View your scheduled posts in the feed. Click "Cancel" if you need to stop a scheduled post.

