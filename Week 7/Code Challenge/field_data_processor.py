import pandas as pd
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
import logging

class FieldDataProcessor:

    def __init__(self, config_params, logging_level="INFO"):
        self.db_path = config_params['db_path']
        self.sql_query = config_params['sql_query']
        self.columns_to_rename = config_params['columns_to_rename']
        self.values_to_rename = config_params['values_to_rename']
        self.weather_map_data = config_params['weather_mapping_csv']

        self.initialize_logging(logging_level)

        # Placeholders
        self.df = None
        self.engine = None

    def initialize_logging(self, logging_level):
        """
        Sets up logging for this instance of FieldDataProcessor.
        """
        logger_name = __name__ + ".FieldDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False  

        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            log_level = logging.INFO
        elif logging_level.upper() == "NONE":  
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO  

        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            ch = logging.StreamHandler()  
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def ingest_sql_data(self):
        self.engine = create_db_engine(self.db_path)
        self.df = query_data(self.engine, self.sql_query)
        self.logger.info("Successfully loaded data.")
        return self.df

    def rename_columns(self):
        """
        Swaps the names of the 'Annual_yield' and 'Crop_type' columns.
        """
        column1, column2 = list(self.columns_to_rename.keys())[0], list(self.columns_to_rename.values())[0]

        temp_name = "__temp_name_for_swap__"
        while temp_name in self.df.columns:
            temp_name += "_"

        self.df = self.df.rename(columns={column1: temp_name})
        self.df = self.df.rename(columns={column2: column1})
        self.df = self.df.rename(columns={temp_name: column2})

        self.logger.info(f"Swapped columns: {column1} <-> {column2}")
        return self.df

    def apply_corrections(self, column_name="Crop_type", abs_column="Elevation"):
        """
        Apply corrections to the DataFrame:
        1. Ensure the specified numeric column has absolute values.
        2. Strip leading/trailing whitespace from categorical values.
        3. Rename values in the categorical column using the mapping provided.
        """
        if abs_column in self.df.columns:
            self.df[abs_column] = self.df[abs_column].abs()

        if column_name in self.df.columns and hasattr(self, "values_to_rename"):
            self.df[column_name] = self.df[column_name].astype(str).str.strip()
            self.df[column_name] = self.df[column_name].replace(self.values_to_rename)

        return self.df

    def weather_station_mapping(self): 
        weather_map_df = read_from_web_CSV(self.weather_map_data)
        self.df = self.df.merge(weather_map_df, on='Field_ID')
        self.df.drop(self.df.columns[self.df.columns.str.contains('Unnamed', case=False)], axis=1, inplace=True)
        return self.df

    def process(self):
        self.df = self.ingest_sql_data()
        self.df = self.rename_columns()
        self.df = self.apply_corrections()
        self.df = self.weather_station_mapping()
        return self.df

