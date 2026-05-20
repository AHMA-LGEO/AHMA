import os
import pandas as pd
import numpy as np
from pathlib import Path

from sqlalchemy import create_engine, inspect, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from utils import transform_geocode_master

# Import all table preparation classes
from section2_prep import Section2DataPrep
from section3_prep import Section3DataPrep
from section4_prep import Section4DataPrep
from section5_prep import Section5DataPrep
from section6_prep import Section6DataPrep
from section7_prep import Section7DataPrep
from section8_prep import Section8DataPrep
from section9_prep import Section9DataPrep
from section10_prep import Section10DataPrep
from section11_prep import Section11DataPrep
from section12_prep import Section12DataPrep


DB_DIR = Path(__file__).parent.parent / "source"

class DBUploader:
    """
    Automated database uploader for census data tables.
    Dynamically creates tables and uploads data from all preparation modules.
    """

    # Define table configurations: {method_name: table_name}
    TABLE_CONFIGS = {
        # Section 2 - Indigenous Communities
        'table_2_1': 'table_2_1_indigenous_territory',
        'table_2_1_1': 'table_2_1_1_nation_links',
        'table_2_2': 'table_2_2_metis_community',

        # Section 3 - Indigenous Population
        'table_3_1_1': 'table_3_1_1_indigenous_pop',
        'table_3_1_2': 'table_3_1_2_indigenous_age',
        'table_3_1_3': 'table_3_1_3_indigenous_location',
        'table_3_1_4': 'table_3_1_4_indigenous_move',
        'table_3_2_3_3': 'table_3_2_3_3_indigenous_age_group',
        'table_3_4': 'table_3_4_indigenous_age_gender',
        'table_3_5': 'table_3_5_indigenous_priority_pop',
        'table_3_5_1': 'table_3_5_1_indigenous_priority_pop_breakdown',
        'table_3_6': 'table_3_6_indigenous_pop_ancestry',

        # Section 4 - Housing Tenure
        'table_4_1': 'table_4_1_housing_tenure',
        'table_4_2': 'table_4_2_housing_tenure_breakdown',
        'table_4_3': 'table_4_3_hh_by_household_size',
        'table_4_4': 'table_4_4_hh_by_household_size_breakdown',

        # Section 5 - Income
        'table_5_1': 'table_5_1_income_shelter_cost',
        'table_5_2': 'table_5_2_hh_amhi_income',
        'table_5_3': 'table_5_3_hh_amhi_income_breakdown',
        'table_5_4': 'table_5_4_median_income',
        'table_5_5_5_6': 'table_5_5_5_6_number_hh_maintainers',

        # Section 6 - Dwellings
        'table_6_1': 'table_6_1_hhs_bedroom',
        'table_6_2': 'table_6_2_hhs_bedroom_breakdown',
        'table_6_3': 'table_6_3_hhs_construction_period',
        'table_6_4': 'table_6_4_hhs_construction_period_breakdown',
        'table_6_5': 'table_6_5_hhs_structure_type',
        'table_6_6': 'table_6_6_hhs_structure_type_breakdown',

        # Section 7 - Shelter Costs and Rental Market
        'table_7_1_7_2': 'table_7_1_7_2_dwelllings',
        'table_7_3_1': 'table_7_3_1_rental_units',
        
        'table_7_3_2_1': 'table_7_3_2_1_average_rent',
        'table_7_3_2_2': 'table_7_3_2_2_change_in_average_rent',
        'table_7_3_3_1': 'table_7_3_3_1_vacancy_rate',
        'table_7_3_3_2': 'table_7_3_3_2_change_in_vacancy_rate',
        

        # Section 8 - Core Housing Need
        'table_8_1': 'table_8_1_core_housing_need',
        'table_8_3': 'table_8_3_hhs_in_chn',
        'table_8_4': 'table_8_4_hhs_in_chn_breakdown',
        'table_8_5': 'table_8_5_hhs_in_chn_prior_pop',
        'table_8_6': 'table_8_6_hhs_in_chn_prior_pop_breakdown',
        'table_8_7': 'table_8_7_housing_deficit',

        # Section 9 - Systemic Pathways and Indigenous Homelessness
        'table_9_1': 'table_9_1_number_corrections',
        'table_9_1_1': 'table_9_1_1_percent_corrections',
        'table_9_2': 'table_9_2_ageing_out_of_care',
        'table_9_3': 'table_9_3_indig_homelessness',

        # Section 10 - Access to Services
        'table_10_1': 'table_10_1_access_services',

        # Section 11 - Population and Household Growth
        'table_11_1_1': 'table_11_1_1_projected_pop',
        'table_11_1_2': 'table_11_1_2_projected_hh',

        # Section 12 - Housing Targets
        'table_12_2': 'table_12_2_indigenous_housing_target'
    }

    def __init__(self, db_path):
        """
        Initialize DB Uploader.

        Args:
            master_geocode_filepath: Path to master geocode Excel file
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Initialize database
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.db_base = declarative_base()
        self.Session = sessionmaker(bind=self.engine)

        # Initialize data preparation classes
        self.section_2_prep = Section2DataPrep()
        self.section_3_prep = Section3DataPrep()
        self.section_4_prep = Section4DataPrep()
        self.section_5_prep = Section5DataPrep()
        self.section_6_prep = Section6DataPrep()
        self.section_7_prep = Section7DataPrep()
        self.section_8_prep = Section8DataPrep()
        self.section_9_prep = Section9DataPrep()
        self.section_10_prep = Section10DataPrep()
        self.section_11_prep = Section11DataPrep()
        self.section_12_prep = Section12DataPrep()

        # Store table classes
        self.table_classes = {}
        self.table_data = {}

    def prepare_geocode_master(self):
        """Load and transform geocode master file"""
        print("Preparing geocode master...")
        master_transformed = transform_geocode_master()
        return master_transformed

    def create_dynamic_table_class(self, table_name, df):
        """
        Dynamically create a SQLAlchemy table class based on DataFrame columns.

        Args:
            table_name: Name for the database table
            df: DataFrame to infer schema from

        Returns:
            SQLAlchemy table class
        """
        columns = {'__tablename__': table_name}

        # Add primary key
        columns['pk'] = Column(Integer, primary_key=True, autoincrement=True)

        # Infer column types from DataFrame
        for col_name in df.columns:
            col_type = df[col_name].dtype

            if pd.api.types.is_integer_dtype(col_type):
                columns[str(col_name)] = Column(Integer)
            elif pd.api.types.is_float_dtype(col_type):
                columns[str(col_name)] = Column(Float)
            else:
                # Default to Text for strings and mixed types
                columns[str(col_name)] = Column(Text)

        # Create the class dynamically
        table_class = type(table_name, (self.db_base,), columns)
        return table_class

    def prepare_all_tables(self):
        """Prepare all tables from data preparation modules"""
        print("=" * 60)
        print("Starting table preparation...")
        print("=" * 60)

        # Geocode master
        self.table_data['geocode_master'] = self.prepare_geocode_master()

        # Section 2
        self.table_data['table_2_1'], self.table_data['table_2_1_1'] = self.section_2_prep.table_2_1()
        self.table_data['table_2_2'] = self.section_2_prep.table_2_2()

        # Section 3
        self.table_data['table_3_1_1'] = self.section_3_prep.table_3_1_1()
        self.table_data['table_3_1_2'] = self.section_3_prep.table_3_1_2()
        self.table_data['table_3_1_3'] = self.section_3_prep.table_3_1_3()
        self.table_data['table_3_1_4'] = self.section_3_prep.table_3_1_4()
        self.table_data['table_3_2_3_3'] = self.section_3_prep.table_3_2_3_3()
        self.table_data['table_3_4'] = self.section_3_prep.table_3_4()
        self.table_data['table_3_5'], self.table_data['table_3_5_1']  = self.section_3_prep.table_3_5_3_5_1()
        self.table_data['table_3_6'] = self.section_3_prep.table_3_6()

        # Section 4
        self.table_data['table_4_1'] = self.section_4_prep.table_4_1()
        self.table_data['table_4_2'] = self.section_4_prep.table_4_2()
        self.table_data['table_4_3'] = self.section_4_prep.table_4_3_4_4("4.3")
        self.table_data['table_4_4'] = self.section_4_prep.table_4_3_4_4("4.4")

        # Section 5
        self.table_data['table_5_1'] = self.section_5_prep.table_5_1()
        self.table_data['table_5_2'] = self.section_5_prep.table_5_2()
        self.table_data['table_5_3'] = self.section_5_prep.table_5_3()
        self.table_data['table_5_4'] = self.section_5_prep.table_5_4()
        self.table_data['table_5_5_5_6'] = self.section_5_prep.table_5_5_5_6()

        # Section 6
        self.table_data['table_6_1'] = self.section_6_prep.table_6_1_6_6("6.1")
        self.table_data['table_6_2'] = self.section_6_prep.table_6_1_6_6("6.2")
        self.table_data['table_6_3'] = self.section_6_prep.table_6_1_6_6("6.3")
        self.table_data['table_6_4'] = self.section_6_prep.table_6_1_6_6("6.4")
        self.table_data['table_6_5'] = self.section_6_prep.table_6_1_6_6("6.5")
        self.table_data['table_6_6'] = self.section_6_prep.table_6_1_6_6("6.6")

        # Section 7
        self.table_data['table_7_1_7_2'] = self.section_7_prep.table_7_1_7_2()
        self.table_data['table_7_3_1'] = self.section_7_prep.table_7_3_1()

        self.table_data['table_7_3_2_1'] = self.section_7_prep.table_7_3_2_1()
        self.table_data['table_7_3_2_2'] = self.section_7_prep.table_7_3_2_2()
        self.table_data['table_7_3_3_1'] = self.section_7_prep.table_7_3_3_1()
        self.table_data['table_7_3_3_2'] = self.section_7_prep.table_7_3_3_2()

        # Section 8
        self.table_data['table_8_1'] = self.section_8_prep.table_8_1()
        self.table_data['table_8_3'] = self.section_8_prep.table_8_3()
        self.table_data['table_8_4'] = self.section_8_prep.table_8_4()
        self.table_data['table_8_5'] = self.section_8_prep.table_8_5()
        self.table_data['table_8_6'] = self.section_8_prep.table_8_6()
        self.table_data['table_8_7'] = self.section_8_prep.table_8_7()

        # Section 9
        self.table_data['table_9_1'] = self.section_9_prep.table_9_1()
        self.table_data['table_9_1_1'] = self.section_9_prep.table_9_1_1()
        self.table_data['table_9_2'] = self.section_9_prep.table_9_2()
        self.table_data['table_9_3'] = self.section_9_prep.table_9_3()

        # Section 10
        self.table_data['table_10_1'] = self.section_10_prep.table_10_1()

        # Section 11
        self.table_data['table_11_1_1'] = self.section_11_prep.table_11_1_1()
        self.table_data['table_11_1_2'] = self.section_11_prep.table_11_1_2()
        
        # Section 12
        self.table_data['table_12_2'] = self.section_12_prep.table_12_2()

        print("\n" + "=" * 60)
        print("All tables prepared successfully!")
        print("=" * 60)

    def create_all_table_classes(self):
        """Create SQLAlchemy table classes for all prepared data"""
        print("\nCreating database table schemas...")

        # Geocode master
        self.table_classes['geocode_master'] = self.create_dynamic_table_class(
            'geocode_master',
            self.table_data['geocode_master']
        )

        # All other tables
        for method_name, table_name in self.TABLE_CONFIGS.items():
            if method_name in self.table_data:
                self.table_classes[method_name] = self.create_dynamic_table_class(
                    table_name,
                    self.table_data[method_name]
                )

        # Create all tables in database
        self.db_base.metadata.create_all(self.engine)

        self.engine.dispose()  # Close all connections

        inspector = inspect(self.engine)
        created_tables = inspector.get_table_names()
        print(f"Created {len(created_tables)} tables in database: {created_tables}")

    def insert_data(self, df, table_class, table_name):
        """
        Insert DataFrame data into database table.

        Args:
            df: DataFrame to insert
            table_class: SQLAlchemy table class
            table_name: Name of table (for logging)
        """
        session = self.Session()

        try:
            # Replace '--' and similar placeholders with NaN
            df = df.replace(["x", "..", "...", "....", "n/a", "N/A", "--", 
                  "xx", "xxx", "xxxx", "xxxxx", "#N/A", "#n/a", '**'], np.nan)

            # Convert DataFrame to list of dictionaries
            records = []
            for _, row in df.iterrows():
                data = {str(k): v for k, v in row.to_dict().items()}
                records.append(table_class(**data))

            if records:
                session.bulk_save_objects(records)
                session.commit()
                print(f"Inserted {len(records)} rows into {table_name}")
            else:
                print(f"NO DATA TO INSERT FOR {table_name}")

        except IntegrityError as e:
            session.rollback()
            print(f"INTEGRITY ERROR in {table_name}: {e}")

        except Exception as e:
            session.rollback()
            print(f"ERROR in {table_name}: {e}")

        finally:
            session.close()

    def upload_all_tables(self):
        """Upload all prepared data to database"""
        print("\n" + "=" * 60)
        print("Starting database upload...")
        print("=" * 60 + "\n")

        # Upload geocode master
        print("Uploading geocode_master...")
        self.insert_data(
            self.table_data['geocode_master'],
            self.table_classes['geocode_master'],
            'geocode_master'
        )

        # Upload all other tables
        for method_name, table_name in self.TABLE_CONFIGS.items():
            if method_name in self.table_data and method_name in self.table_classes:
                print(f"\nUploading {table_name}...")
                self.insert_data(
                    self.table_data[method_name],
                    self.table_classes[method_name],
                    table_name
                )

        print("\n" + "=" * 60)
        print("Database upload complete!")
        print("=" * 60)

    def run(self):
        """Main execution method"""
        self.prepare_all_tables()
        self.create_all_table_classes()
        self.upload_all_tables()


# Usage
if __name__ == "__main__":
    uploader = DBUploader(
        db_path=os.path.join(DB_DIR, "ahma.db")
    )
    uploader.run()