from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np


def _col_as_1d(arr, col_idx_0):
    """
    R-style helper:
    - if arr is 1D, return first n values
    - if arr is 2D, return the requested column
    """
    a = np.asarray(arr, dtype=float)
    if a.ndim == 1:
        return a.copy()
    return a[:, col_idx_0].copy()


def _set_na_r_1_based(vec, start_r, end_r_inclusive=None):
    """
    R-style NA assignment from start_r:end_r_inclusive.
    If end_r_inclusive is None, assign from start_r to end.
    """
    if end_r_inclusive is None:
        end_r_inclusive = len(vec)
    start0 = max(start_r - 1, 0)
    end0 = min(end_r_inclusive, len(vec))
    if start0 < end0:
        vec[start0:end0] = np.nan


def _stacked_bar(ax, bars, colors, labels, ylim=(0, 19)):
    """
    Matplotlib equivalent of R stacked barplot(space = 0, border = NA).

    Safe behavior:
    - trims bars to the number of provided colors/labels
    - avoids IndexError if bars has more rows than expected
    """
    bars = np.asarray(bars, dtype=float)

    if bars.ndim == 1:
        bars = bars.reshape(1, -1)

    n_series = min(bars.shape[0], len(colors), len(labels))
    bars = bars[:n_series, :]

    n_days = bars.shape[1]
    x = np.arange(1, n_days + 1, dtype=float)
    bottom = np.zeros(n_days, dtype=float)

    for i in range(n_series):
        y = np.nan_to_num(bars[i], nan=0.0)
        ax.bar(
            x,
            y,
            width=1.0,
            bottom=bottom,
            color=colors[i],
            edgecolor="none",
            align="edge"
        )
        bottom += y

    ax.set_xlim(1, n_days + 1)
    ax.set_ylim(*ylim)
    ax.set_ylabel(r"Feed intake (kg day$^{-1}$)")
    ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax.legend(labels[:n_series], loc="upper left", frameon=False)


def _limiting_factor_plot(
    ax,
    heatstress,
    coldstress,
    fillgitgraph,
    nelim,
    protgraph,
    genlim,
    maxgr,
    title_x="Age (days)"
):
    x = np.arange(1, maxgr + 1, dtype=float)

    ax.plot(
        x, heatstress[:maxgr],
        linestyle="None", marker="|", color="#D55E00", markersize=7
    )
    ax.plot(
        x, coldstress[:maxgr],
        linestyle="None", marker="|", color="#0072B2", markersize=7
    )
    ax.plot(
        x, fillgitgraph[:maxgr],
        linestyle="None", marker="|", color="#009E73", markersize=7
    )
    ax.plot(
        x, nelim[:maxgr],
        linestyle="None", marker="|", color="#E69F00", markersize=7
    )
    ax.plot(
        x, protgraph[:maxgr],
        linestyle="None", marker="|", color="#CC79A7", markersize=7
    )
    ax.plot(
        x, genlim[:maxgr],
        linestyle="None", marker="|", color="#999999", markersize=7
    )

    ax.set_xlim(1, maxgr)
    ax.set_ylim(0.3, 5.8)
    ax.set_xlabel(title_x)
    ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
    ax.set_yticklabels(
        [
            "protein",
            "energy",
            "digestion cap.",
            "cold stress",
            "heat stress",
            "genotype"
        ]
    )
    ax.tick_params(axis="y", labelrotation=0)


def _pad_to_maxgr(v, maxgr):
    out = np.full(maxgr, np.nan, dtype=float)
    m = min(len(v), maxgr)
    out[:m] = v[:m]
    return out


def generate_output_graphs(
    *,
    BASE_DIR,
    z,
    SCALE,
    TBW,
    TBWBF,
    LIBRARY,
    FEED1QNTY,
    FEED2QNTY,
    FEED3QNTY,
    FEED4QNTY,
    HOUSING1,
    HOUSING,
    ENDDAY,
    REDHP,
    Metheatcold,
    HEATIFEEDMAINTWM,
    FILLGIT,
    PROTBAL,
    FEEDQNTYTOT,
    FEEDQNTY,
    diet_cfg,
    build_feed_plot_components,
    GENLIMdata,
    HEATSTRESSdata,
    COLDSTRESSdata,
    FILLGITGRAPHdata,
    NELIMdata,
    PROTGRAPHdata,
):
    ############################################################
    #                     Graph for cows                       #
    ############################################################

    # 1. TBW over time
    if SCALE == 1:
        maxgr = 1000
    else:
        maxgr = 4000

    fig_cows = plt.figure(figsize=(12, 10))
    gs_cows = GridSpec(3, 1, height_ratios=[1.8, 1.1, 1.4], hspace=0.08)

    ax1 = fig_cows.add_subplot(gs_cows[0])
    ax2 = fig_cows.add_subplot(gs_cows[1], sharex=ax1)
    ax3 = fig_cows.add_subplot(gs_cows[2], sharex=ax1)

    x_cows = np.arange(1, maxgr + 1, dtype=float)

    tbw_cow = _col_as_1d(TBW, 0)
    tbwbf_cow = _col_as_1d(TBWBF, 0)

    ax1.plot(
        x_cows,
        tbw_cow[:maxgr],
        linestyle="-",
        linewidth=1.5,
        color="black",
        label="Genetic potential TBW"
    )
    ax1.plot(
        x_cows,
        tbwbf_cow[:maxgr],
        linestyle="--",
        linewidth=1.5,
        color="black",
        label="Simulated TBW"
    )
    ax1.set_xlim(1, maxgr)
    ax1.set_ylim(0, LIBRARY[12])  # R LIBRARY[13] -> Python index 12
    ax1.set_ylabel("TBW (kg)")
    ax1.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax1.legend(loc="upper left", frameon=False)

    # 2. Feed intake over time
    feed1_cow = _col_as_1d(FEED1QNTY, 0)[:maxgr]
    feed2_cow = _col_as_1d(FEED2QNTY, 0)[:maxgr]
    feed3_cow = _col_as_1d(FEED3QNTY, 0)[:maxgr]

    # FEED4QNTY is not always explicitly created in the Python version.
    # Keep R logic safely: if unavailable, use zeros.
    if FEED4QNTY is not None:
        feed4_cow = _col_as_1d(FEED4QNTY, 0)[:maxgr]
    else:
        feed4_cow = np.zeros(maxgr, dtype=float)

    housing1_cow = _col_as_1d(HOUSING1, 0)[:maxgr] if HOUSING1 is not None else _col_as_1d(HOUSING, 0)[:maxgr]
    common_len_cow = min(len(feed1_cow), len(feed2_cow), len(feed3_cow), len(housing1_cow), maxgr)
    bars, bar_labels, bar_colors = build_feed_plot_components(
        feed1_cow[:common_len_cow],
        feed2_cow[:common_len_cow],
        feed3_cow[:common_len_cow],
        housing1_cow[:common_len_cow],
        diet_cfg,
    )

    # R: bars[, ENDDAY[1]:maxgr] <- NA
    endday1 = int(np.asarray(ENDDAY).reshape(-1)[0])
    if 1 <= endday1 <= common_len_cow:
        bars[:, endday1 - 1:common_len_cow] = np.nan

    _stacked_bar(
        ax2,
        bars,
        colors=bar_colors,
        labels=bar_labels,
        ylim=(0, 19)
    )

    # 3. Defining and limiting factors for growth over time
    HEATSTRESS = np.array(REDHP, dtype=float, copy=True)
    HEATSTRESS[HEATSTRESS < 0] = 4.5
    HEATSTRESS[HEATSTRESS != 4.5] = np.nan

    COLDSTRESS1 = np.array(Metheatcold, dtype=float) - np.array(HEATIFEEDMAINTWM, dtype=float)
    COLDSTRESS = np.array(COLDSTRESS1, dtype=float, copy=True)
    COLDSTRESS[COLDSTRESS > 0] = 3.5
    COLDSTRESS[COLDSTRESS != 3.5] = np.nan

    FILLGITGRAPH = np.array(FILLGIT, dtype=float, copy=True)
    FILLGITGRAPH[FILLGITGRAPH >= 0.97] = 2.5
    FILLGITGRAPH[FILLGITGRAPH != 2.5] = np.nan

    PROTGRAPH = np.array(PROTBAL, dtype=float, copy=True)
    PROTGRAPH[PROTGRAPH < 0] = 0.5
    PROTGRAPH[PROTGRAPH != 0.5] = np.nan
    PROTGRAPH[FILLGITGRAPH >= 0.999] = np.nan

    HEATSTRESS[np.isnan(HEATSTRESS)] = 0
    COLDSTRESS[np.isnan(COLDSTRESS)] = 0
    FILLGITGRAPH[np.isnan(FILLGITGRAPH)] = 0
    PROTGRAPH[np.isnan(PROTGRAPH)] = 0

    TBWBF = np.array(TBWBF, dtype=float, copy=True)
    TBWBF[np.isnan(TBWBF)] = 0

    if bool(diet_cfg.get('scale_feed12_with_tbw_percent', False)):
        # R: FEEDQNTYTOT <- FEEDQNTYTOT[1:(imax[1] + 1)] * TBWBF / 100
        # Python adaptation for current code structure
        feedqnty_tot_work = np.array(FEEDQNTYTOT, dtype=float, copy=True)
        tbwbf_for_feed = _col_as_1d(TBWBF, 0)
        nmin = min(len(feedqnty_tot_work), len(tbwbf_for_feed))
        feedqnty_tot_work = feedqnty_tot_work[:nmin] * tbwbf_for_feed[:nmin] / 100.0
    else:
        feedqnty_tot_work = np.array(FEEDQNTYTOT, dtype=float, copy=True)

    # Cow column
    feedqnty_cow = _col_as_1d(FEEDQNTY, 0)

    nmin = min(
        len(feedqnty_tot_work),
        len(feedqnty_cow),
        len(_col_as_1d(HEATSTRESS, 0)),
        len(_col_as_1d(PROTGRAPH, 0)),
        len(_col_as_1d(FILLGITGRAPH, 0))
    )

    NELIM = feedqnty_tot_work[:nmin] - feedqnty_cow[:nmin]
    NELIM = (
        NELIM
        + _col_as_1d(HEATSTRESS, 0)[:nmin]
        + _col_as_1d(PROTGRAPH, 0)[:nmin]
        + _col_as_1d(FILLGITGRAPH, 0)[:nmin]
    )

    # R source contains: NELIM[NELIM <- 0.00001] <- NA
    # This is not valid as a direct Python condition and also looks like an R typo.
    # To preserve the intended logic used in surrounding lines, the lower threshold is applied as < -0.00001.
    NELIM[NELIM > 0.00001] = np.nan
    NELIM[NELIM < -0.00001] = np.nan
    _set_na_r_1_based(NELIM, endday1, maxgr)

    NELIM[NELIM < 0.00001] = 1.5
    NELIM[NELIM > -0.00001] = 1.5
    NELIM[np.isnan(NELIM)] = 0.0

    GENLIM = (
        _col_as_1d(HEATSTRESS, 0)[:nmin]
        + _col_as_1d(FILLGITGRAPH, 0)[:nmin]
        + _col_as_1d(PROTGRAPH, 0)[:nmin]
        + NELIM
    )
    GENLIM[GENLIM > 0] = np.nan
    GENLIM[GENLIM == 0] = 5.5
    _set_na_r_1_based(GENLIM, endday1, maxgr)

    HEATSTRESS_cow = _col_as_1d(HEATSTRESS, 0)[:nmin]
    COLDSTRESS_cow = _col_as_1d(COLDSTRESS, 0)[:nmin]
    FILLGITGRAPH_cow = _col_as_1d(FILLGITGRAPH, 0)[:nmin]
    PROTGRAPH_cow = _col_as_1d(PROTGRAPH, 0)[:nmin]

    HEATSTRESS_cow[HEATSTRESS_cow == 0] = np.nan
    COLDSTRESS_cow[COLDSTRESS_cow == 0] = np.nan
    FILLGITGRAPH_cow[FILLGITGRAPH_cow == 0] = np.nan
    NELIM[NELIM == 0] = np.nan
    PROTGRAPH_cow[PROTGRAPH_cow == 0] = np.nan

    HEATSTRESS_plot = _pad_to_maxgr(HEATSTRESS_cow, maxgr)
    COLDSTRESS_plot = _pad_to_maxgr(COLDSTRESS_cow, maxgr)
    FILLGITGRAPH_plot = _pad_to_maxgr(FILLGITGRAPH_cow, maxgr)
    NELIM_plot = _pad_to_maxgr(NELIM, maxgr)
    PROTGRAPH_plot = _pad_to_maxgr(PROTGRAPH_cow, maxgr)
    GENLIM_plot = _pad_to_maxgr(GENLIM, maxgr)

    _limiting_factor_plot(
        ax3,
        HEATSTRESS_plot,
        COLDSTRESS_plot,
        FILLGITGRAPH_plot,
        NELIM_plot,
        PROTGRAPH_plot,
        GENLIM_plot,
        maxgr
    )

    fig_cows.savefig(BASE_DIR / f"ligaps_case_{z}_cows.png", dpi=300, bbox_inches="tight")
    plt.close(fig_cows)

    # Lists of the defining and limiting factors
    GENLIMdata       = np.column_stack((GENLIMdata, _pad_to_maxgr(GENLIM, 4000)))
    HEATSTRESSdata   = np.column_stack((HEATSTRESSdata, _pad_to_maxgr(HEATSTRESS_cow, 4000)))
    COLDSTRESSdata   = np.column_stack((COLDSTRESSdata, _pad_to_maxgr(COLDSTRESS_cow, 4000)))
    FILLGITGRAPHdata = np.column_stack((FILLGITGRAPHdata, _pad_to_maxgr(FILLGITGRAPH_cow, 4000)))
    NELIMdata        = np.column_stack((NELIMdata, _pad_to_maxgr(NELIM, 4000)))
    PROTGRAPHdata    = np.column_stack((PROTGRAPHdata, _pad_to_maxgr(PROTGRAPH_cow, 4000)))

    #############################################################################################
    #                     Graph for calves                     #
    ############################################################

    # 1. TBW over time
    maxgr = 1000

    fig_calves = plt.figure(figsize=(12, 10))
    gs_calves = GridSpec(3, 1, height_ratios=[1.8, 1.1, 1.4], hspace=0.08)

    ax1 = fig_calves.add_subplot(gs_calves[0])
    ax2 = fig_calves.add_subplot(gs_calves[1], sharex=ax1)
    ax3 = fig_calves.add_subplot(gs_calves[2], sharex=ax1)

    x_calves = np.arange(1, maxgr + 1, dtype=float)

    tbw_calf = _col_as_1d(TBW, 2)
    tbwbf_calf = _col_as_1d(TBWBF, 2)

    ax1.plot(
        x_calves,
        tbw_calf[:maxgr],
        linestyle="-",
        linewidth=1.5,
        color="black",
        label="Genetic potential TBW"
    )

    endday3 = int(np.asarray(ENDDAY).reshape(-1)[2])
    x_sim_calf = np.arange(1, endday3 + 1, dtype=float)
    ax1.plot(
        x_sim_calf,
        tbwbf_calf[:endday3],
        linestyle="--",
        linewidth=1.5,
        color="black",
        label="Simulated TBW"
    )

    ax1.set_xlim(1, maxgr)
    ax1.set_ylim(0, LIBRARY[12])  # R LIBRARY[13]
    ax1.set_ylabel("TBW (kg)")
    ax1.tick_params(axis="x", which="both", bottom=False, labelbottom=False)
    ax1.legend(loc="upper left", frameon=False)

    # 2. feed intake over time
    feed1_calf = _col_as_1d(FEED1QNTY, 2)[:maxgr] if np.asarray(FEED1QNTY).ndim == 2 else _col_as_1d(FEED1QNTY, 0)[:maxgr]
    feed2_calf = _col_as_1d(FEED2QNTY, 2)[:maxgr] if np.asarray(FEED2QNTY).ndim == 2 else _col_as_1d(FEED2QNTY, 0)[:maxgr]
    feed3_calf = _col_as_1d(FEED3QNTY, 2)[:maxgr] if np.asarray(FEED3QNTY).ndim == 2 else _col_as_1d(FEED3QNTY, 0)[:maxgr]

    if FEED4QNTY is not None:
        feed4_calf = _col_as_1d(FEED4QNTY, 2)[:maxgr] if np.asarray(FEED4QNTY).ndim == 2 else _col_as_1d(FEED4QNTY, 0)[:maxgr]
    else:
        feed4_calf = np.zeros_like(feed1_calf, dtype=float)

    housing_calf = _col_as_1d(HOUSING, 0)

    # force all calf feed vectors to the same usable length
    common_len = min(
        len(feed1_calf),
        len(feed2_calf),
        len(feed3_calf),
        len(feed4_calf),
        len(housing_calf),
        maxgr
    )

    feed1_calf = feed1_calf[:common_len]
    feed2_calf = feed2_calf[:common_len]
    feed3_calf = feed3_calf[:common_len]
    feed4_calf = feed4_calf[:common_len]
    housing_calf = housing_calf[:common_len]

    bars, bar_labels, bar_colors = build_feed_plot_components(
        feed1_calf,
        feed2_calf,
        feed3_calf,
        housing_calf,
        diet_cfg,
    )

    # apply ENDDAY masking using the actual plotted length
    if 1 <= endday3 <= common_len:
        bars[:, endday3 - 1:common_len] = np.nan

    _stacked_bar(
        ax2,
        bars,
        colors=bar_colors,
        labels=bar_labels,
        ylim=(0, 19)
    )

    # 3. Defining and limiting factors for growth over time
    HEATSTRESS = np.array(REDHP, dtype=float, copy=True)
    HEATSTRESS[HEATSTRESS < 0] = 4.5
    HEATSTRESS[HEATSTRESS != 4.5] = np.nan

    COLDSTRESS1 = np.array(Metheatcold, dtype=float) - np.array(HEATIFEEDMAINTWM, dtype=float)
    COLDSTRESS = np.array(COLDSTRESS1, dtype=float, copy=True)
    COLDSTRESS[COLDSTRESS > 0] = 3.5
    COLDSTRESS[COLDSTRESS != 3.5] = np.nan

    FILLGITGRAPH = np.array(FILLGIT, dtype=float, copy=True)
    FILLGITGRAPH[FILLGITGRAPH >= 0.97] = 2.5
    FILLGITGRAPH[FILLGITGRAPH != 2.5] = np.nan

    PROTGRAPH = np.array(PROTBAL, dtype=float, copy=True)
    PROTGRAPH[PROTGRAPH < 0] = 0.5
    PROTGRAPH[PROTGRAPH != 0.5] = np.nan
    PROTGRAPH[FILLGITGRAPH >= 0.999] = np.nan

    HEATSTRESS[np.isnan(HEATSTRESS)] = 0
    COLDSTRESS[np.isnan(COLDSTRESS)] = 0
    FILLGITGRAPH[np.isnan(FILLGITGRAPH)] = 0
    PROTGRAPH[np.isnan(PROTGRAPH)] = 0

    TBWBF = np.array(TBWBF, dtype=float, copy=True)
    TBWBF[np.isnan(TBWBF)] = 0

    if bool(diet_cfg.get('scale_feed12_with_tbw_percent', False)):
        feedqnty_tot_work = np.array(FEEDQNTYTOT, dtype=float, copy=True)
        if feedqnty_tot_work.ndim == 1:
            tbwbf_for_feed = _col_as_1d(TBWBF, 0)
            nmin2 = min(len(feedqnty_tot_work), len(tbwbf_for_feed))
            feedqnty_tot_work = feedqnty_tot_work[:nmin2] * tbwbf_for_feed[:nmin2] / 100.0
        else:
            feedqnty_tot_work = feedqnty_tot_work * TBWBF / 100.0
    else:
        feedqnty_tot_work = np.array(FEEDQNTYTOT, dtype=float, copy=True)

    # R: NELIM <- c(rep(FEEDQNTYTOT[1:4000], 9)) - FEEDQNTY
    # Python adaptation:
    if np.asarray(feedqnty_tot_work).ndim == 1:
        base = np.array(feedqnty_tot_work[:4000], dtype=float)
        if np.asarray(FEEDQNTY).ndim == 2:
            n_animals = np.asarray(FEEDQNTY).shape[1]
            nelim_base = np.tile(base.reshape(-1, 1), (1, n_animals))
        else:
            nelim_base = base.copy()
    else:
        nelim_base = np.array(feedqnty_tot_work, dtype=float)

    NELIM = nelim_base - np.array(FEEDQNTY, dtype=float)
    NELIM = NELIM + HEATSTRESS + PROTGRAPH + FILLGITGRAPH

    NELIM[NELIM > 0.00001] = np.nan
    NELIM[NELIM < -0.00001] = np.nan

    NELIM[NELIM < 0.00001] = 1.5
    NELIM[NELIM > -0.00001] = 1.5

    if np.asarray(NELIM).ndim == 2:
        if 1 <= endday3 <= min(maxgr, NELIM.shape[0]):
            NELIM[endday3 - 1:maxgr, :] = np.nan
    else:
        _set_na_r_1_based(NELIM, endday3, maxgr)

    NELIM[np.isnan(NELIM)] = 0.0

    GENLIM = HEATSTRESS + FILLGITGRAPH + PROTGRAPH + NELIM
    GENLIM[GENLIM > 0] = np.nan
    GENLIM[GENLIM == 0] = 5.5

    if np.asarray(GENLIM).ndim == 2:
        if 1 <= endday3 <= min(maxgr, GENLIM.shape[0]):
            GENLIM[endday3 - 1:maxgr, :] = np.nan
    else:
        _set_na_r_1_based(GENLIM, endday3, maxgr)

    HEATSTRESS_calf = _col_as_1d(HEATSTRESS, 2 if np.asarray(HEATSTRESS).ndim == 2 else 0)
    COLDSTRESS_calf = _col_as_1d(COLDSTRESS, 2 if np.asarray(COLDSTRESS).ndim == 2 else 0)
    FILLGITGRAPH_calf = _col_as_1d(FILLGITGRAPH, 2 if np.asarray(FILLGITGRAPH).ndim == 2 else 0)
    NELIM_calf = _col_as_1d(NELIM, 2 if np.asarray(NELIM).ndim == 2 else 0)
    PROTGRAPH_calf = _col_as_1d(PROTGRAPH, 2 if np.asarray(PROTGRAPH).ndim == 2 else 0)
    GENLIM_calf = _col_as_1d(GENLIM, 2 if np.asarray(GENLIM).ndim == 2 else 0)

    HEATSTRESS_calf[HEATSTRESS_calf == 0] = np.nan
    COLDSTRESS_calf[COLDSTRESS_calf == 0] = np.nan
    FILLGITGRAPH_calf[FILLGITGRAPH_calf == 0] = np.nan
    NELIM_calf[NELIM_calf == 0] = np.nan
    PROTGRAPH_calf[PROTGRAPH_calf == 0] = np.nan

    _limiting_factor_plot(
        ax3,
        _pad_to_maxgr(HEATSTRESS_calf, maxgr),
        _pad_to_maxgr(COLDSTRESS_calf, maxgr),
        _pad_to_maxgr(FILLGITGRAPH_calf, maxgr),
        _pad_to_maxgr(NELIM_calf, maxgr),
        _pad_to_maxgr(PROTGRAPH_calf, maxgr),
        _pad_to_maxgr(GENLIM_calf, maxgr),
        maxgr
    )

    fig_calves.savefig(BASE_DIR / f"ligaps_case_{z}_calves.png", dpi=300, bbox_inches="tight")
    plt.close(fig_calves)

    # End of the graph for calves

    #############################################################################################

    return (
        GENLIMdata,
        HEATSTRESSdata,
        COLDSTRESSdata,
        FILLGITGRAPHdata,
        NELIMdata,
        PROTGRAPHdata,
    )
