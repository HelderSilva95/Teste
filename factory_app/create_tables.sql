-- Factory Work Tracking System - Create Tables
-- Execute este script no SQL Server para criar todas as tabelas
-- IMPORTANTE: Ajuste o nome da base de dados conforme necessário

USE factory_db;
GO

-- ========== Tabela de Setores ==========
IF OBJECT_ID('sectors', 'U') IS NULL
BEGIN
    CREATE TABLE sectors (
        id INT PRIMARY KEY IDENTITY(1,1),
        code NVARCHAR(50) NOT NULL UNIQUE,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX),
        location NVARCHAR(100),
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_sectors_code ON sectors(code);
    CREATE INDEX idx_sectors_is_active ON sectors(is_active);
    PRINT 'Tabela sectors criada';
END
GO

-- ========== Tabela de Utilizadores ==========
IF OBJECT_ID('users', 'U') IS NULL
BEGIN
    CREATE TABLE users (
        id INT PRIMARY KEY IDENTITY(1,1),
        username NVARCHAR(50) NOT NULL UNIQUE,
        email NVARCHAR(100) UNIQUE,
        full_name NVARCHAR(100) NOT NULL,
        hashed_password NVARCHAR(255) NOT NULL,
        role NVARCHAR(20) NOT NULL DEFAULT 'operador' CHECK (role IN ('operador', 'supervisor', 'gestor', 'admin')),
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_users_username ON users(username);
    CREATE INDEX idx_users_role ON users(role);
    CREATE INDEX idx_users_is_active ON users(is_active);
    PRINT 'Tabela users criada';
END
GO

-- ========== Tabela de Máquinas ==========
IF OBJECT_ID('machines', 'U') IS NULL
BEGIN
    CREATE TABLE machines (
        id INT PRIMARY KEY IDENTITY(1,1),
        code NVARCHAR(50) NOT NULL UNIQUE,
        name NVARCHAR(100) NOT NULL,
        description NVARCHAR(MAX),
        location NVARCHAR(100),
        sector_id INT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (sector_id) REFERENCES sectors(id)
    );
    CREATE INDEX idx_machines_code ON machines(code);
    CREATE INDEX idx_machines_sector_id ON machines(sector_id);
    CREATE INDEX idx_machines_is_active ON machines(is_active);
    PRINT 'Tabela machines criada';
END
GO

-- ========== Tabelas de Associação Many-to-Many ==========
-- Associação User <-> Sector
IF OBJECT_ID('user_sectors', 'U') IS NULL
BEGIN
    CREATE TABLE user_sectors (
        user_id INT NOT NULL,
        sector_id INT NOT NULL,
        PRIMARY KEY (user_id, sector_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (sector_id) REFERENCES sectors(id) ON DELETE CASCADE
    );
    CREATE INDEX idx_user_sectors_user ON user_sectors(user_id);
    CREATE INDEX idx_user_sectors_sector ON user_sectors(sector_id);
    PRINT 'Tabela user_sectors criada';
END
GO

-- Associação User <-> Machine
IF OBJECT_ID('user_machines', 'U') IS NULL
BEGIN
    CREATE TABLE user_machines (
        user_id INT NOT NULL,
        machine_id INT NOT NULL,
        PRIMARY KEY (user_id, machine_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (machine_id) REFERENCES machines(id) ON DELETE CASCADE
    );
    CREATE INDEX idx_user_machines_user ON user_machines(user_id);
    CREATE INDEX idx_user_machines_machine ON user_machines(machine_id);
    PRINT 'Tabela user_machines criada';
END
GO

-- ========== Tabela de Ordens de Trabalho ==========
IF OBJECT_ID('work_orders', 'U') IS NULL
BEGIN
    CREATE TABLE work_orders (
        id INT PRIMARY KEY IDENTITY(1,1),
        order_number NVARCHAR(50) NOT NULL UNIQUE,
        external_order_id NVARCHAR(100),
        product_code NVARCHAR(50) NOT NULL,
        product_description NVARCHAR(MAX),
        quantity_planned FLOAT NOT NULL,
        quantity_completed FLOAT NOT NULL DEFAULT 0,
        unit NVARCHAR(10) NOT NULL DEFAULT 'UN',
        machine_id INT,
        priority INT NOT NULL DEFAULT 5,
        planned_start DATETIME2,
        planned_end DATETIME2,
        actual_start DATETIME2,
        actual_end DATETIME2,
        status NVARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
        notes NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (machine_id) REFERENCES machines(id)
    );
    CREATE INDEX idx_work_orders_number ON work_orders(order_number);
    CREATE INDEX idx_work_orders_status ON work_orders(status);
    CREATE INDEX idx_work_orders_machine ON work_orders(machine_id);
    PRINT 'Tabela work_orders criada';
END
GO

-- ========== Tabela de Logs de Produção ==========
IF OBJECT_ID('production_logs', 'U') IS NULL
BEGIN
    CREATE TABLE production_logs (
        id INT PRIMARY KEY IDENTITY(1,1),
        work_order_id INT NOT NULL,
        machine_id INT NOT NULL,
        operator1_id INT NOT NULL,
        operator2_id INT,
        start_time DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        end_time DATETIME2,
        setup_time INT DEFAULT 0,
        pause_time INT DEFAULT 0,
        quantity_input FLOAT,
        quantity_output FLOAT,
        status NVARCHAR(20) NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'paused', 'completed')),
        notes NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (machine_id) REFERENCES machines(id),
        FOREIGN KEY (operator1_id) REFERENCES users(id),
        FOREIGN KEY (operator2_id) REFERENCES users(id)
    );
    CREATE INDEX idx_production_logs_work_order ON production_logs(work_order_id);
    CREATE INDEX idx_production_logs_machine ON production_logs(machine_id);
    CREATE INDEX idx_production_logs_status ON production_logs(status);
    CREATE INDEX idx_production_logs_operators ON production_logs(operator1_id, operator2_id);
    PRINT 'Tabela production_logs criada';
END
GO

-- ========== Tabela de Pausas de Produção ==========
IF OBJECT_ID('production_pauses', 'U') IS NULL
BEGIN
    CREATE TABLE production_pauses (
        id INT PRIMARY KEY IDENTITY(1,1),
        production_log_id INT NOT NULL,
        pause_start DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        pause_end DATETIME2,
        reason NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (production_log_id) REFERENCES production_logs(id) ON DELETE CASCADE
    );
    CREATE INDEX idx_production_pauses_log ON production_pauses(production_log_id);
    PRINT 'Tabela production_pauses criada';
END
GO

-- ========== Tabela de Inventário ==========
IF OBJECT_ID('inventory_items', 'U') IS NULL
BEGIN
    CREATE TABLE inventory_items (
        id INT PRIMARY KEY IDENTITY(1,1),
        qr_code NVARCHAR(100) NOT NULL UNIQUE,
        material_type NVARCHAR(20) NOT NULL CHECK (material_type IN ('chapa', 'solido', 'materia_prima', 'outro')),
        material_name NVARCHAR(100) NOT NULL,
        color NVARCHAR(50),
        dimensions NVARCHAR(100),
        thickness FLOAT,
        quantity FLOAT NOT NULL DEFAULT 1,
        unit NVARCHAR(10) NOT NULL DEFAULT 'UN',
        location NVARCHAR(100),
        supplier NVARCHAR(100),
        entry_date DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        status NVARCHAR(20) NOT NULL DEFAULT 'disponivel' CHECK (status IN ('disponivel', 'reservado', 'em_uso', 'consumido')),
        notes NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    CREATE INDEX idx_inventory_qr_code ON inventory_items(qr_code);
    CREATE INDEX idx_inventory_type ON inventory_items(material_type);
    CREATE INDEX idx_inventory_status ON inventory_items(status);
    PRINT 'Tabela inventory_items criada';
END
GO

-- ========== Tabela de Consumo de Materiais ==========
IF OBJECT_ID('material_consumption', 'U') IS NULL
BEGIN
    CREATE TABLE material_consumption (
        id INT PRIMARY KEY IDENTITY(1,1),
        production_log_id INT NOT NULL,
        inventory_item_id INT NOT NULL,
        quantity_consumed FLOAT NOT NULL,
        consumption_date DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        notes NVARCHAR(MAX),
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (production_log_id) REFERENCES production_logs(id),
        FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id)
    );
    CREATE INDEX idx_material_consumption_production ON material_consumption(production_log_id);
    CREATE INDEX idx_material_consumption_inventory ON material_consumption(inventory_item_id);
    PRINT 'Tabela material_consumption criada';
END
GO

-- ========== Tabela de Não-Conformidades ==========
IF OBJECT_ID('non_compliances', 'U') IS NULL
BEGIN
    CREATE TABLE non_compliances (
        id INT PRIMARY KEY IDENTITY(1,1),
        nc_number NVARCHAR(50) NOT NULL UNIQUE,
        nc_type NVARCHAR(20) NOT NULL CHECK (nc_type IN ('qualidade', 'processo', 'material', 'equipamento', 'seguranca', 'outro')),
        severity NVARCHAR(20) NOT NULL CHECK (severity IN ('baixa', 'media', 'alta', 'critica')),
        description NVARCHAR(MAX) NOT NULL,
        work_order_id INT,
        production_log_id INT,
        machine_id INT,
        reported_by_id INT NOT NULL,
        detected_date DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        status NVARCHAR(20) NOT NULL DEFAULT 'aberta' CHECK (status IN ('aberta', 'em_analise', 'resolvida', 'fechada')),
        resolution NVARCHAR(MAX),
        resolved_by_id INT,
        resolved_date DATETIME2,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
        FOREIGN KEY (production_log_id) REFERENCES production_logs(id),
        FOREIGN KEY (machine_id) REFERENCES machines(id),
        FOREIGN KEY (reported_by_id) REFERENCES users(id),
        FOREIGN KEY (resolved_by_id) REFERENCES users(id)
    );
    CREATE INDEX idx_non_compliances_number ON non_compliances(nc_number);
    CREATE INDEX idx_non_compliances_type ON non_compliances(nc_type);
    CREATE INDEX idx_non_compliances_severity ON non_compliances(severity);
    CREATE INDEX idx_non_compliances_status ON non_compliances(status);
    PRINT 'Tabela non_compliances criada';
END
GO

PRINT '';
PRINT '=========================================';
PRINT 'Todas as tabelas foram criadas com sucesso!';
PRINT '=========================================';
GO
