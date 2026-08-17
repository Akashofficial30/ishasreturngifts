-- PostgreSQL Setup Script for Isha Return Gifts
-- Run this as a superuser (e.g., postgres)

-- Create database
CREATE DATABASE isha_return_gifts;

-- Create user
CREATE USER isha_user WITH PASSWORD 'isha@2025';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE isha_return_gifts TO isha_user;

-- Connect to the database
\c isha_return_gifts

-- Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO isha_user;

