# Dhulikona Foundation DBMS for Jal Jeevan Mission

## Project Overview

This project is aimed at developing a Database Management System (DBMS) for the Dhulikona Foundation in Uttar Pradesh to support the **Jal Jeevan Mission**. The mission focuses on providing clean drinking water to rural households by addressing issues such as arsenic contamination. The system ensures efficient communication, tracking, and monitoring to streamline the delivery of clean water. 

## Team Members

- **Bhaskar Anand** (USN: 4NI22CS037)
- **Anand Daga** (USN: 4NI22CS023)

## Problem Statement

The current system used by the foundation relies on manual methods and rudimentary digital tools, leading to delays in communication, inefficient tracking of water supply operations, and poor maintenance of water supply systems. This project aims to build an automated system to address these inefficiencies.

## Key Features

1. **Real-time Data Tracking**  
   Real-time updates on pump operation, water quality, and supply frequency for improved decision-making.
   
2. **Efficient Communication**  
   Streamlined communication between stakeholders to ensure timely problem resolution and information sharing.

3. **Comprehensive Monitoring**  
   Systematic monitoring of all stages of the water supply process, from construction to post-implementation.

4. **Maintenance Management**  
   Efficient tracking of maintenance activities, with notifications for unresolved issues.

5. **User-friendly Interface**  
   Designed to be easy to use for stakeholders of all technical skill levels.


## Tech Stack Used:
- **Database Management System:** SQLite3
- **Backend Framework:** Python (Django)
- **Frontend Framework:** HTML, Bootstrap CSS


## Installation Guide

1. **Clone the Repository**
   ```bash
   https://github.com/bhaskar-nie/Dhulikona_Project.git
   ```

2. **Install Required Packages**
   Ensure you have Python and Django installed. Run the following command to install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Database**
   Run the following command to apply migrations and set up the database:
   ```bash
   python manage.py migrate
   ```

4. **Run the Development Server**
   To start the server and access the system locally:
   ```bash
   python manage.py runserver
   ```

5. **Access the System**
   Open a web browser and go to `http://127.0.0.1:8000` to access the system.

## Usage

- **Admin Panel**: Administrators can log in to manage users, update water quality data, track pump operations, and view reports.
- **Real-time Monitoring**: Stakeholders can access real-time data on water supply and pump status.

## Future Enhancements

- **IoT Integration**: Integration of IoT devices for automatic water quality monitoring.
- **Mobile Application**: Mobile app development for on-the-go tracking and issue management.
- **Advanced Analytics**: Implementation of predictive analytics for maintenance and efficiency reports.

## Contributing

We welcome contributions from the community! If you would like to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push the branch (`git push origin feature-branch`).
5. Open a Pull Request.
