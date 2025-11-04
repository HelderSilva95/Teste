-- Factory Work Tracking System - Create Tables
-- Execute este script no SQL Server para criar todas as tabelas

USE factory_db;
GO

-- Tabela de Utilizadores
IF OBJECT_ID('users', 'U') IS NULL
BEGIN
    CREATE TABLE users (
        id INT PRIMARY KEY IDENTITY(1,1),
        username NVARCHAR(50) NOT NULL UNIQUE,
        email NVARCHAR(100) UNIQUE,
        full_name NVARCHAR(100) NOT NULL,
        hashed_password NVARCHAR(255) NOT NULL,
        role NVARCHAR(20) NOT NULL DEFAULT 'operador',
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_users_username ON users(username);
    CREATE INDEX idx_users_role ON users(role);
    PRINT 'Tabela users criada';
END
GO

-- Tabela de Máquinas
IF OBJECT_ID('machines', 'U') IS NULL
BEGIN
    CREATE TABLE machines (
        id INT PRIMARY KEY IDENTITY(1,1),
        code NVARCHAR(50) NOT NULL UNIQUE,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX),
        location NVARCHAR(100),
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_machines_code ON machines(code);
    PRINT 'Tabela machines criada';
END
GO

-- Tabela de Ordens de Trabalho
IF OBJECT_ID('work_orders', 'U') IS NULL
BEGIN
    CREATE TABLE work_orders (
        id INT PRIMARY KEY IDENTITY(1,1),
        order_number NVARCHAR(50) NOT NULL UNIQUE,
        external_order_id NVARCHAR(50),
        product_code NVARCHAR(50) NOT NULL,
        product_description NVARCHAR(MAX),
        quantity_planned FLOAT NOT NULL,
        quantity_produced FLOAT NOT NULL DEFAULT 0,
        unit NVARCHAR(20) NOT NULL DEFAULT 'UN',
        machine_id INT,
        status NVARCHAR(20) NOT NULL DEFAULT 'pending',
        priority INT NOT NULL DEFAULT 5,
        planned_start DATETIME2,
        planned_end DATETIME2,
        actual_start DATETIME2,
        actual_end DATETIME2,
        notes NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (machine_id) REFERENCES machines(id)
    );
    CREATE INDEX idx_work_orders_number ON work_orders(order_number);
    CREATE INDEX idx_work_orders_status ON work_orders(status);
    CREATE INDEX idx_work_orders_priority ON work_orders(priority);
    PRINT 'Tabela work_orders criada';
END
GO

-- Tabela de Inventário
IF OBJECT_ID('inventory_items', 'U') IS NULL
BEGIN
    CREATE TABLE inventory_items (
        id INT PRIMARY KEY IDENTITY(1,1),
        qr_code NVARCHAR(100) NOT NULL UNIQUE,
        material_type NVARCHAR(20) NOT NULL,
        material_name NVARCHAR(100) NOT NULL,
        color NVARCHAR(50),
        finish NVARCHAR(50),
        length FLOAT,
        width FLOAT,
        thickness FLOAT,
        quantity FLOAT NOT NULL DEFAULT 1,
        unit NVARCHAR(20) NOT NULL DEFAULT 'UN',
        location NVARCHAR(100),
        status NVARCHAR(20) NOT NULL DEFAULT 'available',
        supplier NVARCHAR(100),
        batch_number NVARCHAR(50),
        received_date DATETIME2,
        last_used_date DATETIME2,
        notes NVARCHAR(MAX),
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_inventory_qr ON inventory_items(qr_code);
    CREATE INDEX idx_inventory_status ON inventory_items(status);
    PRINT 'Tabela inventory_items criada';
END
GO

-- Tabela de Logs de Produção
IF OBJECT_ID('production_logs', 'U') IS NULL
BEGIN
    CREATE TABLE production_logs (
        id INT PRIMARY KEY IDENTITY(1,1),
        work_order_id INT NOT NULL,
        machine_id INT NOT NULL,
        operator1_id INT NOT NULL,
        operator2_id INT,
        start_time DATETIME2 NOT NULL,
        end_time DATETIME2,
        setup_time INT,
        pause_time INT DEFAULT 0,
        quantity_input FLOAT,
        quantity_output FLOAT,
        unit NVARCHAR(20) DEFAULT 'UN',
        status NVARCHAR(20) NOT NULL DEFAULT 'in_progress',
        notes NVARCHAR(MAX),
        pause_reason NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (machine_id) REFERENCES machines(id),
        FOREIGN KEY (operator1_id) REFERENCES users(id),
        FOREIGN KEY (operator2_id) REFERENCES users(id)
    );
    CREATE INDEX idx_production_status ON production_logs(status);
    CREATE INDEX idx_production_workorder ON production_logs(work_order_id);
    PRINT 'Tabela production_logs criada';
END
GO

-- Tabela de Pausas de Produção
IF OBJECT_ID('production_pauses', 'U') IS NULL
BEGIN
    CREATE TABLE production_pauses (
        id INT PRIMARY KEY IDENTITY(1,1),
        production_log_id INT NOT NULL,
        pause_start DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        pause_end DATETIME2,
        reason NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (production_log_id) REFERENCES production_logs(id)
    );
    CREATE INDEX idx_pauses_production ON production_pauses(production_log_id);
    PRINT 'Tabela production_pauses criada';
END
GO

-- Tabela de Consumo de Materiais
IF OBJECT_ID('material_consumptions', 'U') IS NULL
BEGIN
    CREATE TABLE material_consumptions (
        id INT PRIMARY KEY IDENTITY(1,1),
        production_log_id INT NOT NULL,
        inventory_item_id INT NOT NULL,
        work_order_id INT NOT NULL,
        quantity_consumed FLOAT NOT NULL,
        consumed_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        notes NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (production_log_id) REFERENCES production_logs(id),
        FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id),
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id)
    );
    CREATE INDEX idx_consumption_production ON material_consumptions(production_log_id);
    PRINT 'Tabela material_consumptions criada';
END
GO

-- Tabela de Não-Conformidades
IF OBJECT_ID('non_compliances', 'U') IS NULL
BEGIN
    CREATE TABLE non_compliances (
        id INT PRIMARY KEY IDENTITY(1,1),
        nc_number NVARCHAR(50) NOT NULL UNIQUE,
        nc_type NVARCHAR(20) NOT NULL,
        severity NVARCHAR(20) NOT NULL,
        status NVARCHAR(20) NOT NULL DEFAULT 'open',
        work_order_id INT,
        machine_id INT,
        production_log_id INT,
        reported_by_id INT NOT NULL,
        assigned_to_id INT,
        title NVARCHAR(200) NOT NULL,
        description NVARCHAR(MAX) NOT NULL,
        root_cause NVARCHAR(MAX),
        corrective_action NVARCHAR(MAX),
        preventive_action NVARCHAR(MAX),
        occurred_at DATETIME2 NOT NULL,
        reported_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        resolved_at DATETIME2,
        closed_at DATETIME2,
        estimated_cost INT,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (machine_id) REFERENCES machines(id),
        FOREIGN KEY (production_log_id) REFERENCES production_logs(id),
        FOREIGN KEY (reported_by_id) REFERENCES users(id),
        FOREIGN KEY (assigned_to_id) REFERENCES users(id)
    );
    CREATE INDEX idx_nc_number ON non_compliances(nc_number);
    CREATE INDEX idx_nc_status ON non_compliances(status);
    CREATE INDEX idx_nc_severity ON non_compliances(severity);
    PRINT 'Tabela non_compliances criada';
END
GO

PRINT '';
PRINT '=== TABELAS CRIADAS COM SUCESSO ===';
PRINT 'Total: 8 tabelas';
PRINT '';
PRINT 'Próximo passo: Execute init_database.py para criar dados iniciais';
GO
