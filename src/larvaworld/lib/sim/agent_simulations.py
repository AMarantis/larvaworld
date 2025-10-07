from __future__ import annotations

import random

import numpy as np
from typing import Any, Optional


from .. import reg, util
from ..param import Larva_Distro

__all__: list[str] = [
    "sim_model",
    "sim_models",
]

__displayname__ = "Individual agent simulations"


def sim_models(modelIDs: list[str], colors: Optional[list[str]] = None, groupIDs: Optional[list[str]] = None, lgs: Optional[list[Any]] = None, data_dir: Optional[str] = None, **kwargs: Any):
    N = len(modelIDs)
    if colors is None:
        colors = util.N_colors(N)
    if groupIDs is None:
        groupIDs = modelIDs
    if lgs is None:
        lgs = [None] * N
    if data_dir is None:
        dirs = [None] * N
    else:
        dirs = [f"{data_dir}/{dID}" for dID in groupIDs]
    ds = [
        sim_model(
            mID=modelIDs[i],
            color=colors[i],
            dataset_id=groupIDs[i],
            lg=lgs[i],
            dir=dirs[i],
            **kwargs,
        )
        for i in range(N)
    ]
    return ds


def sim_model(
    mID: str,
    Nids: int = 1,
    refID: Optional[str] = None,
    refDataset: Optional[Any] = None,
    imitation: bool = False,
    tor_durs: list[int] = [],
    dsp_starts: list[int] = [0],
    dsp_stops: list[int] = [40],
    enrichment: bool = True,
    parameter_dict: dict[str, Any] = {},
    lg: Optional[Any] = None,
    env_params: dict[str, Any] = {},
    dir: Optional[str] = None,
    duration: float = 3,
    dt: float = 1 / 16,
    color: str = "blue",
    dataset_id: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    Nticks = int(duration * 60 / dt)
    if refDataset is None and refID is not None:
        refID = refDataset.refID
    if lg is None:
        lg = reg.larvagroup.LarvaGroup(
            group_id=dataset_id,
            model=mID,
            color=color,
            distribution=Larva_Distro(N=Nids),
            sample=refID,
            imitation=imitation,
        )
    ids, p0s, fo0s, ms = lg.generate_agent_attrs(parameter_dict)
    s, e = sim_multi_agents(
        Nticks, Nids, ms, lg.group_id, dt=dt, ids=ids, p0s=p0s, fo0s=fo0s
    )

    c_kws = {
        "dir": dir,
        "id": lg.group_id,
        "larva_group": lg,
        "env_params": env_params,
        "Npoints": 3,
        "Ncontour": 0,
        "fr": 1 / dt,
    }
    from ...process.dataset import LarvaDataset

    d = LarvaDataset(**c_kws, load_data=False)
    d.set_data(step=s, end=e)
    if enrichment:
        d = d.enrich(
            proc_keys=["spatial", "angular", "dispersion", "tortuosity"],
            anot_keys=["bout_detection", "bout_distribution", "interference"],
            dsp_starts=dsp_starts,
            dsp_stops=dsp_stops,
            tor_durs=tor_durs,
        )

    return d


def sim_single_agent(m: Any, Nticks: int = 1000, dt: float = 0.1, df_columns: Optional[list[str]] = None, p0: Optional[tuple[float, float]] = None, fo0: Optional[float] = None):
    from ..model import Locomotor, BaseController

    if fo0 is None:
        fo0 = 0.0
    if p0 is None:
        p0 = (0.0, 0.0)
    x0, y0 = p0
    if df_columns is None:
        df_columns = reg.getPar(
            ["b", "fo", "ro", "fov", "I_T", "x", "y", "d", "v", "A_T", "A_CT"]
        )
    AA = np.ones([Nticks, len(df_columns)]) * np.nan

    controller = BaseController(**m.physics)
    l = m.body.length
    bend_errors = 0
    DL = Locomotor(dt=dt, conf=m.brain)
    for qq in range(100):
        if random.uniform(0, 1) < 0.5:
            DL.step(A_in=0, length=l)
    b, fo, ro, fov, x, y, dst, v = 0, fo0, 0, 0, x0, y0, 0, 0
    for i in range(Nticks):
        lin, ang, feed = DL.step(A_in=0, length=l)
        v = lin * controller.lin_vel_coef
        fov += (
            -controller.ang_damping * fov
            - controller.body_spring_k * b
            + ang * controller.torque_coef
        ) * dt

        d_or = fov * dt
        if np.abs(d_or) > np.pi:
            bend_errors += 1
        dst = v * dt
        d_ro = controller.compute_delta_rear_angle(b, dst, l)
        b = util.wrap_angle_to_0(b + d_or - d_ro)
        fo = (fo + d_or) % (2 * np.pi)
        ro = (ro + d_ro) % (2 * np.pi)
        x += dst * np.cos(fo)
        y += dst * np.sin(fo)

        AA[i, :] = [
            b,
            fo,
            ro,
            fov,
            DL.turner.input,
            x,
            y,
            dst,
            v,
            DL.turner.output,
            DL.interference.cur_attenuation,
        ]

    AA[:, :4] = np.rad2deg(AA[:, :4])
    return AA


def sim_multi_agents(Nticks: int, Nids: int, ms: list[Any], group_id: str, dt: float = 0.1, ids: Optional[list[str]] = None, p0s: Optional[list[tuple[float, float]]] = None, fo0s: Optional[list[float]] = None):
    df_columns = reg.getPar(
        ["b", "fo", "ro", "fov", "I_T", "x", "y", "d", "v", "A_T", "A_CT"]
    )
    if ids is None:
        ids = [f"{group_id}{j}" for j in range(Nids)]
    if p0s is None:
        p0s = [(0.0, 0.0) for j in range(Nids)]
    if fo0s is None:
        fo0s = [0.0 for j in range(Nids)]
    my_index = pd.MultiIndex.from_product(
        [np.arange(Nticks), ids], names=["Step", "AgentID"]
    )
    AA = np.ones([Nticks, Nids, len(df_columns)]) * np.nan

    for j, id in enumerate(ids):
        m = ms[j]
        AA[:, j, :] = sim_single_agent(
            m, Nticks, dt=dt, df_columns=df_columns, p0=p0s[j], fo0=fo0s[j]
        )

    AA = AA.reshape(Nticks * Nids, len(df_columns))
    s = pd.DataFrame(AA, index=my_index, columns=df_columns)
    s = s.astype(float)

    e = pd.DataFrame(index=ids)
    e.index = e.index.set_names(["AgentID"])
    e["cum_dur"] = Nticks * dt
    e["num_ticks"] = Nticks
    e["length"] = [m.body.length for m in ms]

    return s, e
