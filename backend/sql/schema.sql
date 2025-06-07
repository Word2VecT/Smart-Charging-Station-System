-- backend/sql/schema.sql

-- Drop existing tables and types to ensure a clean slate.
-- CASCADE will drop any dependent objects as well.
DROP TABLE IF EXISTS OperationalReports CASCADE;
DROP TABLE IF EXISTS ChargingOrders CASCADE;
DROP TABLE IF EXISTS ChargingRequests CASCADE;
DROP TABLE IF EXISTS ChargingPiles CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS PileLogs CASCADE;

DROP TYPE IF EXISTS UserRole;
DROP TYPE IF EXISTS PileType;
DROP TYPE IF EXISTS PileStatus;
DROP TYPE IF EXISTS RequestType;
DROP TYPE IF EXISTS RequestStatus;
DROP TYPE IF EXISTS ReportType;

-- Enum Types
CREATE TYPE UserRole AS ENUM ('user', 'admin');
CREATE TYPE PileType AS ENUM ('FAST', 'TRICKLE');
CREATE TYPE PileStatus AS ENUM ('AVAILABLE', 'CHARGING', 'FAULTY', 'OFF');
CREATE TYPE RequestType AS ENUM ('FAST', 'TRICKLE');
CREATE TYPE RequestStatus AS ENUM ('WAITING', 'CHARGING', 'FINISHED', 'CANCELLED');
CREATE TYPE ReportType AS ENUM ('DAILY', 'WEEKLY', 'MONTHLY');


-- Users Table
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    registration_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    role UserRole NOT NULL DEFAULT 'user'
);

-- Charging Piles Table
CREATE TABLE ChargingPiles (
    pile_id SERIAL PRIMARY KEY,
    pile_code VARCHAR(10) UNIQUE NOT NULL,
    type PileType NOT NULL,
    status PileStatus NOT NULL DEFAULT 'OFF',
    power_rate DECIMAL(10, 2) NOT NULL
);

-- Charging Requests/Queue Information Table
CREATE TABLE ChargingRequests (
    request_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    queue_number VARCHAR(20) UNIQUE,
    requested_charge_type RequestType NOT NULL,
    requested_charge_amount DECIMAL(10, 2) NOT NULL,
    status RequestStatus NOT NULL DEFAULT 'WAITING',
    request_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    assigned_pile_id INTEGER REFERENCES ChargingPiles(pile_id),
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ
);

-- Charging Orders/Bills Table
CREATE TABLE ChargingOrders (
    order_id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES ChargingRequests(request_id),
    user_id INTEGER NOT NULL REFERENCES Users(user_id),
    pile_id INTEGER NOT NULL REFERENCES ChargingPiles(pile_id),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    actual_charge_amount DECIMAL(10, 2) NOT NULL,
    charge_fee DECIMAL(10, 2) NOT NULL,
    service_fee DECIMAL(10, 2) NOT NULL,
    total_fee DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Operational Reports Data Table
CREATE TABLE OperationalReports (
    report_id SERIAL PRIMARY KEY,
    report_type ReportType NOT NULL,
    report_date DATE NOT NULL,
    pile_id INTEGER REFERENCES ChargingPiles(pile_id), -- Can be NULL for overall reports
    total_charges INTEGER NOT NULL,
    total_charging_duration_seconds BIGINT NOT NULL,
    total_energy_consumed_kwh DECIMAL(15, 2) NOT NULL,
    total_charge_fee DECIMAL(15, 2) NOT NULL,
    total_service_fee DECIMAL(15, 2) NOT NULL,
    total_revenue DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_type, report_date, pile_id)
);

-- Indexes for performance
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_charging_requests_status ON ChargingRequests(status);
CREATE INDEX idx_charging_requests_user_id ON ChargingRequests(user_id);
CREATE INDEX idx_charging_orders_user_id ON ChargingOrders(user_id);
CREATE INDEX idx_charging_orders_pile_id ON ChargingOrders(pile_id);
CREATE INDEX idx_operational_reports_date ON OperationalReports(report_date); 