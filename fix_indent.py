f = open('/app/pages/0_ML_Dashboard.py')
c = f.read()
f.close()

# The for loop body lost its indentation - fix it
c = c.replace(
    '        for model_name, vals in metrics.items():\n        rows.append(',
    '        for model_name, vals in metrics.items():\n            if not isinstance(vals, dict):\n                continue\n            rows.append('
)

f = open('/app/pages/0_ML_Dashboard.py', 'w')
f.write(c)
f.close()
print('DONE')
