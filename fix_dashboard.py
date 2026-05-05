f = open('/app/pages/0_ML_Dashboard.py')
c = f.read()
f.close()

# Remove the bad fix first, then apply correct one
c = c.replace('        if not isinstance(vals, dict): continue\n        rows.append(', '        rows.append(')

# Now apply correct fix inside the for loop properly
old = '''    if metrics:
        rows = []
        for model_name, vals in metrics.items():
            rows.append('''

new = '''    if metrics:
        rows = []
        for model_name, vals in metrics.items():
            if not isinstance(vals, dict):
                continue
            rows.append('''

c = c.replace(old, new)

f = open('/app/pages/0_ML_Dashboard.py', 'w')
f.write(c)
f.close()
print('DONE - 0_ML_Dashboard fixed')
