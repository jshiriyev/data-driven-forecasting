import matplotlib.pyplot as plt

# total number of wells = 364
# total number of oil producer wells is 339
# total number of gas producer wells is 105
# total number of water injection wells is 53

labels = ['Water Injector', 'Gas Producer', 'Oil Producer']
sizes = [53, 105, 339]
colors = ['#66b3ff','#99ff99','#ff9999']
explode = (0.1, 0.1, 0.1)  # Explode the 1st slice (i.e. 'Category A')

# Create a pie chart
fig, ax = plt.subplots()

def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d}'.format(v=val)
    return my_format
    
ax.pie(
    sizes,
    explode=explode,
    labels=labels,
    colors=colors,
    shadow=True,
    startangle=140,
    autopct=autopct_format(sizes)
)

# Equal aspect ratio ensures that pie is drawn as a circle.
ax.axis('equal')  

# Add a title
plt.title('Well Stock History')

# Display the chart
plt.show()
