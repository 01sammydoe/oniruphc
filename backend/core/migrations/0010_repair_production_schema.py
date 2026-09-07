from django.db import migrations


def repair_columns(apps, schema_editor):
	connection = schema_editor.connection
	introspection = connection.introspection
	with connection.cursor() as cursor:
		columns_by_table = {
			table: {column.name for column in introspection.get_table_description(cursor, table)}
			for table in ('core_appointment', 'core_nursevitals')
			if table in introspection.table_names(cursor)
		}

	appointment = apps.get_model('core', 'Appointment')
	nurse_vitals = apps.get_model('core', 'NurseVitals')
	fields_by_table = {
		'core_appointment': (appointment, ('price', 'payment_status', 'paid_at')),
		'core_nursevitals': (nurse_vitals, ('recent_test_result', 'diagnosis')),
	}
	for table, (model, field_names) in fields_by_table.items():
		missing = set(field_names) - columns_by_table.get(table, set())
		for field_name in missing:
			field = model._meta.get_field(field_name).clone()
			if field_name in ('recent_test_result', 'diagnosis'):
				field.default = ''
			schema_editor.add_field(model, field)


class Migration(migrations.Migration):
	dependencies = [
		('core', '0009_doctorconsultation'),
	]

	operations = [
		migrations.RunPython(repair_columns, migrations.RunPython.noop),
	]