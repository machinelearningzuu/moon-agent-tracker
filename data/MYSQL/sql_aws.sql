USE moon_agent_tracker;

SELECT * 
FROM agents;

SELECT * 
FROM branches;

SELECT * 
FROM products;

SELECT * 
FROM sales;

SELECT * 
FROM teams;

SELECT *
FROM notifications;

-- DROP TABLE sales;
-- DROP TABLE products;
-- DROP TABLE agents;
-- DROP TABLE branches;
-- DROP TABLE teams;
-- DROP TABLE notifications;


CREATE TABLE notifications (
    notification_id VARCHAR(255) PRIMARY KEY,
    recipient_id VARCHAR(255),
    type VARCHAR(50),
    title VARCHAR(255),
    message TEXT,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at DATETIME NOT NULL,
    sent_at DATETIME NULL,
    FOREIGN KEY (recipient_id) REFERENCES agents(agent_id)
);


INSERT INTO notifications (
    notification_id,
    recipient_id,
    type,
    title,
    message,
    status,
    created_at,
    sent_at
)
VALUES (
    'notif_gen_013',
    'A505270',
    'GENERAL',
    'Reminder: Monthly Performance Review',
    'Please review your performance for the month of March.',
    'PENDING',
    DATE_SUB(NOW(), INTERVAL 1 DAY),
    NULL
);