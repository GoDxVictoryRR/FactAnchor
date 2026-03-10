-- Create the schema for financial records (mock business data)
CREATE TABLE IF NOT EXISTS financial_results (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    quarter VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value_numeric NUMERIC(15,2),
    value_text VARCHAR(255)
);

-- Clear existing data if run multiple times
TRUNCATE TABLE financial_results RESTART IDENTITY CASCADE;

-- Insert 20 verifiable realistic financial data points for Meridian Corp.
INSERT INTO financial_results (company_name, quarter, year, metric_name, value_numeric, value_text) VALUES
('Meridian Corp', 'Q3', 2025, 'Revenue', 4500000000.00, '$4.5B'),
('Meridian Corp', 'Q3', 2025, 'Operating Margin', 22.50, '22.5%'),
('Meridian Corp', 'Q3', 2025, 'Headcount', 14500, '14,500 employees'),
('Meridian Corp', 'Q3', 2025, 'Cash Balance', 8200000000.00, '$8.2B'),
('Meridian Corp', 'Q3', 2025, 'R&D Spend', 675000000.00, '$675M'),
('Meridian Corp', 'Q3', 2025, 'R&D As Pct Revenue', 15.00, '15%'),
('Meridian Corp', 'Q3', 2025, 'Net Income', 950000000.00, '$950M'),
('Meridian Corp', 'Q3', 2025, 'EPS', 2.15, '$2.15 per share'),
('Meridian Corp', 'Q3', 2025, 'Customer Growth', 12.40, '12.4% y/y'),
('Meridian Corp', 'Q2', 2025, 'Revenue', 4200000000.00, '$4.2B'),
('Meridian Corp', 'Q2', 2025, 'Operating Margin', 21.00, '21.0%'),
('Meridian Corp', 'Q1', 2025, 'Revenue', 4000000000.00, '$4.0B'),
('Meridian Corp', 'Q4', 2024, 'Revenue', 4600000000.00, '$4.6B'),
('Meridian Corp', 'Q4', 2024, 'Headcount', 13200, '13,200 employees'),
('Meridian Corp', 'Q4', 2024, 'Cash Balance', 7500000000.00, '$7.5B'),
('Meridian Corp', 'Q4', 2024, 'Operating Margin', 23.20, '23.2%'),
('Meridian Corp', 'Q4', 2024, 'R&D Pct Revenue', 14.50, '14.5%'),
('Meridian Corp', 'Q4', 2024, 'Net Income', 1100000000.00, '$1.1B'),
('Meridian Corp', 'Q4', 2024, 'Customer Retention', 98.20, '98.2%'),
('Meridian Corp', 'Q3', 2024, 'Revenue', 3800000000.00, '$3.8B');
