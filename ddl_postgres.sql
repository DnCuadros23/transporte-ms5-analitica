CREATE TABLE IF NOT EXISTS usuarios (
  id                INTEGER PRIMARY KEY,
  nombre            VARCHAR(100),
  apellido          VARCHAR(100),
  email             VARCHAR(150),
  telefono          VARCHAR(20),
  distrito          VARCHAR(60),
  fecha_nacimiento  DATE,
  fecha_registro    TIMESTAMP,
  activo            BOOLEAN
);

CREATE TABLE IF NOT EXISTS conductores (
  id                     INTEGER PRIMARY KEY,
  nombre                 VARCHAR(100),
  apellido               VARCHAR(100),
  email                  VARCHAR(150),
  telefono               VARCHAR(20),
  nro_licencia           VARCHAR(30),
  distrito_base          VARCHAR(60),
  fecha_ingreso          DATE,
  calificacion_promedio  NUMERIC(3,2),
  activo                 BOOLEAN
);

CREATE TABLE IF NOT EXISTS vehiculos (
  id             INTEGER PRIMARY KEY,
  conductor_id   INTEGER REFERENCES conductores(id),
  placa          VARCHAR(10),
  marca          VARCHAR(50),
  modelo         VARCHAR(50),
  anio           INTEGER,
  color          VARCHAR(30),
  capacidad      INTEGER,
  tipo_servicio  VARCHAR(20)
);
