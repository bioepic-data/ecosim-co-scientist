-- HWSD2 DuckDB Schema
-- FAO Harmonized World Soil Database v2.0
-- Schema reverse-engineered from CSV files

-- =============================================================================
-- DOMAIN / LOOKUP TABLES
-- =============================================================================

-- Additional Properties (Gelic, Vertic, etc.)
CREATE TABLE D_ADD_PROP (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Available Water Capacity codes
CREATE TABLE D_AWC (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Data source coverage codes
CREATE TABLE D_COVERAGE (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Drainage class codes
CREATE TABLE D_DRAINAGE (
    SYMBOL VARCHAR,
    CODE VARCHAR PRIMARY KEY,
    VALUE VARCHAR
);

-- FAO 1990 soil classification
CREATE TABLE D_FAO90 (
    SYMBOL VARCHAR,
    CODE VARCHAR PRIMARY KEY,
    VALUE VARCHAR
);

-- Impermeable layer codes
CREATE TABLE D_IL (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Köppen-Geiger climate classification
CREATE TABLE D_KOPPEN (
    CODE VARCHAR PRIMARY KEY,
    VALUE VARCHAR
);

-- Soil phase codes (Stony, Lithic, Petric, etc.)
CREATE TABLE D_PHASE (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Root obstacle depth codes
CREATE TABLE D_ROOTS (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Root depth categories
CREATE TABLE D_ROOT_DEPTH (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Soil wetness regime codes
CREATE TABLE D_SWR (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- Texture class codes (general)
CREATE TABLE D_TEXTURE (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- SOTER texture classification
CREATE TABLE D_TEXTURE_SOTER (
    CODE VARCHAR PRIMARY KEY,
    VALUE VARCHAR
);

-- USDA texture classification
CREATE TABLE D_TEXTURE_USDA (
    CODE INTEGER PRIMARY KEY,
    VALUE VARCHAR
);

-- WRB 2-digit codes
CREATE TABLE D_WRB2 (
    CODE VARCHAR PRIMARY KEY,
    VALUE VARCHAR
);

-- WRB 2-digit numeric codes
CREATE TABLE D_WRB2code (
    CODE VARCHAR PRIMARY KEY,
    VALUE VARCHAR
);

-- WRB 4-digit codes
CREATE TABLE D_WRB4 (
    ID INTEGER PRIMARY KEY,
    VALUE VARCHAR,
    CODE VARCHAR
);

-- WRB phases (detailed classification)
CREATE TABLE D_WRB_PHASES (
    ID INTEGER PRIMARY KEY,
    CODE VARCHAR,
    VALUE VARCHAR
);

-- =============================================================================
-- WRB CLASSIFICATION TABLES
-- =============================================================================

-- WRB soil classes with RGB colors for visualization
CREATE TABLE WRB_Class (
    ID INTEGER PRIMARY KEY,
    ID_Class INTEGER,
    ClassNumber INTEGER,
    Divider INTEGER,
    Label VARCHAR,
    Symbol VARCHAR,
    Red INTEGER,
    Green INTEGER,
    Blue INTEGER
);

-- WRB layer metadata
CREATE TABLE WRB_Layer (
    ID INTEGER PRIMARY KEY,
    ID_AezLibrary INTEGER,
    LayerName VARCHAR,
    Filename VARCHAR,
    Units VARCHAR,
    Bytes INTEGER,
    Multiplier INTEGER,
    ZeroIsValue INTEGER,
    ID_Class_Type INTEGER,
    ID_Class INTEGER
);

-- WRB library reference
CREATE TABLE WRB_Library (
    ID_AezLibrary INTEGER PRIMARY KEY,
    AezLibrary VARCHAR,
    FileName VARCHAR
);

-- =============================================================================
-- MAIN DATA TABLES
-- =============================================================================

-- Soil Mapping Units (SMU) - Summary level data
CREATE TABLE HWSD2_SMU (
    ID INTEGER PRIMARY KEY,
    HWSD2_SMU_ID INTEGER NOT NULL,
    WISE30s_SMU_ID VARCHAR,
    HWSD1_SMU_ID INTEGER,
    COVERAGE INTEGER,  -- references D_COVERAGE
    SHARE DECIMAL(5,2),  -- percentage
    WRB4 VARCHAR,  -- references D_WRB4
    WRB_PHASES VARCHAR,  -- references D_WRB_PHASES
    WRB2 VARCHAR,  -- references D_WRB2
    WRB2_CODE VARCHAR,  -- references D_WRB2code
    FAO90 VARCHAR,  -- references D_FAO90
    KOPPEN VARCHAR,  -- references D_KOPPEN
    TEXTURE_USDA INTEGER,  -- references D_TEXTURE_USDA
    REF_BULK_DENSITY DOUBLE,  -- g/cm³
    BULK_DENSITY DOUBLE,  -- g/cm³
    DRAINAGE VARCHAR,  -- references D_DRAINAGE
    ROOT_DEPTH INTEGER,  -- references D_ROOT_DEPTH
    AWC DOUBLE,  -- mm/m
    PHASE1 INTEGER,  -- references D_PHASE
    PHASE2 INTEGER,  -- references D_PHASE
    ROOTS INTEGER,  -- references D_ROOTS
    IL INTEGER,  -- references D_IL
    ADD_PROP INTEGER  -- references D_ADD_PROP
);

-- Detailed soil layers with physical and chemical properties
CREATE TABLE HWSD2_LAYERS (
    ID INTEGER PRIMARY KEY,
    HWSD2_SMU_ID INTEGER NOT NULL,
    NSC_MU_SOURCE1 VARCHAR,  -- National Soil Classification
    NSC_MU_SOURCE2 VARCHAR,  -- National Soil Classification
    WISE30s_SMU_ID VARCHAR,
    HWSD1_SMU_ID INTEGER,
    COVERAGE INTEGER,  -- references D_COVERAGE
    SEQUENCE INTEGER,  -- Sequence in SMU
    SHARE DECIMAL(5,2),  -- percentage
    NSC VARCHAR,
    WRB_PHASES VARCHAR,  -- references D_WRB_PHASES
    WRB4 VARCHAR,  -- references D_WRB4
    WRB2 VARCHAR,  -- references D_WRB2
    FAO90 VARCHAR,  -- references D_FAO90
    ROOT_DEPTH VARCHAR,  -- references D_ROOT_DEPTH
    PHASE1 INTEGER,  -- references D_PHASE
    PHASE2 INTEGER,  -- references D_PHASE
    ROOTS INTEGER,  -- references D_ROOTS
    IL INTEGER,  -- references D_IL
    SWR INTEGER,  -- references D_SWR
    DRAINAGE VARCHAR,  -- references D_DRAINAGE
    AWC VARCHAR,  -- Available Water Capacity, mm
    ADD_PROP INTEGER,  -- references D_ADD_PROP

    -- Layer depth information
    LAYER VARCHAR,  -- Layer code (D1-D7)
    TOPDEP INTEGER,  -- Top depth, cm
    BOTDEP INTEGER,  -- Bottom depth, cm

    -- Physical properties
    COARSE DOUBLE,  -- % volume coarse fragments
    SAND DOUBLE,  -- % weight
    SILT DOUBLE,  -- % weight
    CLAY DOUBLE,  -- % weight
    TEXTURE_USDA INTEGER,  -- references D_TEXTURE_USDA
    TEXTURE_SOTER VARCHAR,  -- references D_TEXTURE_SOTER
    BULK DOUBLE,  -- Bulk density, g/cm³
    REF_BULK DOUBLE,  -- Reference bulk density, g/cm³

    -- Chemical properties
    ORG_CARBON DOUBLE,  -- Organic carbon, % weight
    PH_WATER DOUBLE,  -- pH in water, -log(H+)
    TOTAL_N DOUBLE,  -- Total nitrogen, g/kg
    CN_RATIO DOUBLE,  -- Carbon/Nitrogen ratio

    -- Cation exchange properties
    CEC_SOIL DOUBLE,  -- CEC soil, cmolc/kg
    CEC_CLAY DOUBLE,  -- CEC clay, cmolc/kg
    CEC_EFF DOUBLE,  -- ECEC, cmolc/kg
    TEB DOUBLE,  -- Total Exchangeable Bases, cmolc/kg
    BSAT DOUBLE,  -- Base saturation, % CECsoil
    ALUM_SAT DOUBLE,  -- Aluminium saturation, % ECEC
    ESP DOUBLE,  -- Exchangeable Sodium Percentage, %

    -- Other chemical properties
    TCARBON_EQ DOUBLE,  -- Calcium carbonate, % weight
    GYPSUM DOUBLE,  -- Gypsum content, % weight
    ELEC_COND DOUBLE  -- Electric conductivity, dS/m
);

-- =============================================================================
-- METADATA TABLES (keep as reference documentation)
-- =============================================================================

CREATE TABLE HWSD2_LAYERS_METADATA (
    ID INTEGER PRIMARY KEY,
    FIELD VARCHAR,
    UNIT VARCHAR,
    DESCRIPTION VARCHAR,
    DATATYPE VARCHAR,
    DOMAIN VARCHAR
);

CREATE TABLE HWSD2_SMU_METADATA (
    ID INTEGER PRIMARY KEY,
    FIELD VARCHAR,
    UNIT VARCHAR,
    DESCRIPTION VARCHAR,
    DATATYPE VARCHAR,
    DOMAIN VARCHAR
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Indexes on main tables
CREATE INDEX idx_layers_smu_id ON HWSD2_LAYERS(HWSD2_SMU_ID);
CREATE INDEX idx_layers_wise30s ON HWSD2_LAYERS(WISE30s_SMU_ID);
CREATE INDEX idx_layers_hwsd1 ON HWSD2_LAYERS(HWSD1_SMU_ID);
CREATE INDEX idx_layers_coverage ON HWSD2_LAYERS(COVERAGE);
CREATE INDEX idx_layers_layer ON HWSD2_LAYERS(LAYER);

CREATE INDEX idx_smu_hwsd2_id ON HWSD2_SMU(HWSD2_SMU_ID);
CREATE INDEX idx_smu_wise30s ON HWSD2_SMU(WISE30s_SMU_ID);
CREATE INDEX idx_smu_hwsd1 ON HWSD2_SMU(HWSD1_SMU_ID);
CREATE INDEX idx_smu_coverage ON HWSD2_SMU(COVERAGE);

-- =============================================================================
-- DATA LOADING COMMANDS
-- =============================================================================

-- Load domain tables
COPY D_ADD_PROP FROM 'HWSD2_csv/D_ADD_PROP.csv' (HEADER TRUE, DELIMITER ',');
COPY D_AWC FROM 'HWSD2_csv/D_AWC.csv' (HEADER TRUE, DELIMITER ',');
COPY D_COVERAGE FROM 'HWSD2_csv/D_COVERAGE.csv' (HEADER TRUE, DELIMITER ',');
COPY D_DRAINAGE FROM 'HWSD2_csv/D_DRAINAGE.csv' (HEADER TRUE, DELIMITER ',');
COPY D_FAO90 FROM 'HWSD2_csv/D_FAO90.csv' (HEADER TRUE, DELIMITER ',');
COPY D_IL FROM 'HWSD2_csv/D_IL.csv' (HEADER TRUE, DELIMITER ',');
COPY D_KOPPEN FROM 'HWSD2_csv/D_KOPPEN.csv' (HEADER TRUE, DELIMITER ',');
COPY D_PHASE FROM 'HWSD2_csv/D_PHASE.csv' (HEADER TRUE, DELIMITER ',');
COPY D_ROOTS FROM 'HWSD2_csv/D_ROOTS.csv' (HEADER TRUE, DELIMITER ',');
COPY D_ROOT_DEPTH FROM 'HWSD2_csv/D_ROOT_DEPTH.csv' (HEADER TRUE, DELIMITER ',');
COPY D_SWR FROM 'HWSD2_csv/D_SWR.csv' (HEADER TRUE, DELIMITER ',');
COPY D_TEXTURE FROM 'HWSD2_csv/D_TEXTURE.csv' (HEADER TRUE, DELIMITER ',');
COPY D_TEXTURE_SOTER FROM 'HWSD2_csv/D_TEXTURE_SOTER.csv' (HEADER TRUE, DELIMITER ',');
COPY D_TEXTURE_USDA FROM 'HWSD2_csv/D_TEXTURE_USDA.csv' (HEADER TRUE, DELIMITER ',');
COPY D_WRB2 FROM 'HWSD2_csv/D_WRB2.csv' (HEADER TRUE, DELIMITER ',');
COPY D_WRB2code FROM 'HWSD2_csv/D_WRB2code.csv' (HEADER TRUE, DELIMITER ',');
COPY D_WRB4 FROM 'HWSD2_csv/D_WRB4.csv' (HEADER TRUE, DELIMITER ',');
COPY D_WRB_PHASES FROM 'HWSD2_csv/D_WRB_PHASES.csv' (HEADER TRUE, DELIMITER ',');

-- Load WRB tables
COPY WRB_Class FROM 'HWSD2_csv/WRB_Class.csv' (HEADER TRUE, DELIMITER ',');
COPY WRB_Layer FROM 'HWSD2_csv/WRB_Layer.csv' (HEADER TRUE, DELIMITER ',');
COPY WRB_Library FROM 'HWSD2_csv/WRB_Library.csv' (HEADER TRUE, DELIMITER ',');

-- Load metadata tables
COPY HWSD2_LAYERS_METADATA FROM 'HWSD2_csv/HWSD2_LAYERS_METADATA.csv' (HEADER TRUE, DELIMITER ',');
COPY HWSD2_SMU_METADATA FROM 'HWSD2_csv/HWSD2_SMU_METADATA.csv' (HEADER TRUE, DELIMITER ',');

-- Load main data tables (these are large, ~400k and ~30k rows)
COPY HWSD2_LAYERS FROM 'HWSD2_csv/HWSD2_LAYERS.csv' (HEADER TRUE, DELIMITER ',', NULL '');
COPY HWSD2_SMU FROM 'HWSD2_csv/HWSD2_SMU.csv' (HEADER TRUE, DELIMITER ',', NULL '');
