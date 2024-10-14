import pandas as pd


wells_data = {
    'well_id': [1, 2, 3, 4, 5, 6],
    'well_row': [1, 1, 1, 1, 2, 2],
    'well_column': [1, 2, 3, 4, 1, 2],
    'plate_id': [101, 101, 101, 101, 102, 102],
    'property_name': ['concentration', 'concentration', 'concentration', 'concentration', 'concentration', 'concentration'],
    'property_value': ['1', '2', '3', None, None, None]
}

plates_data = {
    'plate_id': [101, 102],
    'experiment_id': [1001, 1002],
    'property_name': ['channel', 'channel'],
    'property_value': ['1', '1']
}

experiments_data = {
    'experiment_id': [1001, 1002],
    'property_name': ['concentration_unit', 'concentration_unit'],
    'property_value': ['ul', 'ul']
}

wells_df = pd.DataFrame(wells_data)
plates_df = pd.DataFrame(plates_data)
experiments_df = pd.DataFrame(experiments_data)

wells_pivot = wells_df.pivot(index=['well_id', 'well_row', 'well_column', 'plate_id'], 
                             columns='property_name', 
                             values='property_value').reset_index()

plates_pivot = plates_df.pivot(index='plate_id', 
                               columns='property_name', 
                               values='property_value').reset_index()

merged_wells_plates = pd.merge(wells_pivot, plates_pivot, how='left', on='plate_id')

experiments_pivot = experiments_df.pivot(index='experiment_id', 
                                         columns='property_name', 
                                         values='property_value').reset_index()

merged_wells_plates_experiments = pd.merge(merged_wells_plates, 
                                           plates_df[['plate_id', 'experiment_id']], 
                                           how='left', on='plate_id')
final_df = pd.merge(merged_wells_plates_experiments, experiments_pivot, 
                    how='left', on='experiment_id')

for column in final_df.columns:
    if column not in ['well_id', 'well_row', 'well_column', 'experiment_id', 'plate_id']:
        final_df[column] = final_df[column].fillna(final_df[column + '_x']).fillna(final_df[column + '_y'])

final_df = final_df.drop(columns=['experiment_id', 'plate_id'])

final_df.to_excel("result.xlsx", index=False)

print("Result saved to result.xlsx")