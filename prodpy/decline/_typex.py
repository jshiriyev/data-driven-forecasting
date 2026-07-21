import matplotlib.pyplot as plt


def TypeCurve(prod, RES_ABB):

    df = prod[prod['Reservoir Abbreviation'] == RES_ABB].copy()

    df['months_on_prod'] = (
        (df['production_date'].dt.year - df['First Production Date'].dt.year) * 12 +
        (df['production_date'].dt.month - df['First Production Date'].dt.month)
    )

    df['q_norm'] = df['oil_bbl'] / df.groupby('api14')['oil_bbl'].transform('max')

    p10 = df.groupby('months_on_prod')['q_norm'].quantile(0.9).reset_index()
    p50 = df.groupby('months_on_prod')['q_norm'].quantile(0.5).reset_index()
    p90 = df.groupby('months_on_prod')['q_norm'].quantile(0.1).reset_index()

    p10['q_smooth'] = p10['q_norm'].rolling(7, center=True).mean()
    p50['q_smooth'] = p50['q_norm'].rolling(7, center=True).mean()
    p90['q_smooth'] = p90['q_norm'].rolling(7, center=True).mean()

    p10_factor = 900_000 / p10['q_smooth'].sum()
    p50_factor = 550_000 / p50['q_smooth'].sum()
    p90_factor = 300_000 / p90['q_smooth'].sum()

    fig, ax = plt.subplots(figsize=(14, 4))

    for key, grp in df.groupby(['api14']):
        ax.plot(grp['months_on_prod'], grp['oil_bbl'], label=key, color='gray', alpha=0.5)

    ax.plot(p10['months_on_prod'], p10['q_smooth']*p10_factor, label='P10', linestyle='dashed', color = 'red', alpha=0.5)
    ax.plot(p50['months_on_prod'], p50['q_smooth']*p50_factor, label='P50', linestyle='solid', color = 'blue', alpha=1.0)
    ax.plot(p90['months_on_prod'], p90['q_smooth']*p90_factor, label='P90', linestyle='dashed', color = 'red', alpha=0.5)

    ax.set_ylabel('Monthly Oil Rate (BBL)')
    ax.set_ylim(bottom=0)
    ax.grid(visible=True, which='major', axis='both', color='gray', linestyle='--', linewidth=0.5)
    ax.tick_params(axis='x', length=0)

    return p10, p50, p90, ax