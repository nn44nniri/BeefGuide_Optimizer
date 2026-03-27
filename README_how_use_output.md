The climate optimizer should use this (x_2) as a **moving reference** for closed-loop control, not as a direct command.

So the loop becomes:

[
\text{sensors} \rightarrow z_t
\quad,\quad
x_2 \rightarrow \text{reference bands}
\quad,\quad
\text{climate optimizer} \rightarrow u_t
]

where:

* (z_t): current measured environment from sensors
* (x_2): daily target demands from BeefMPC-Guide
* (u_t): actuator commands for heater, cooler, damper

For your example, the references are:

[
T^{ref}=[14,18]^\circ C,\quad RH^{ref}=[55,70]%,\quad V^{ref}=[0.4,0.9]\ \text{m/s}
]

and the priority is:

[
\text{reduce cold stress to preserve energy for gain}
]

That means the lower controller should mainly act to keep the barn from becoming too cold, because cold stress is currently the main biological loss mechanism.

## How to use it in feedback form

At each control step, for example every 1 minute or 5 minutes, the climate optimizer reads the sensors:

[
T_t,\ RH_t,\ V_t
]

Then it compares them with the target bands from (x_2).

Define band errors like this:

[
e_T =
\begin{cases}
14 - T_t & T_t < 14 \
0 & 14 \le T_t \le 18 \
18 - T_t & T_t > 18
\end{cases}
]

[
e_{RH} =
\begin{cases}
55 - RH_t & RH_t < 55 \
0 & 55 \le RH_t \le 70 \
70 - RH_t & RH_t > 70
\end{cases}
]

[
e_V =
\begin{cases}
0.4 - V_t & V_t < 0.4 \
0 & 0.4 \le V_t \le 0.9 \
0.9 - V_t & V_t > 0.9
\end{cases}
]

These errors tell the controller whether the process is outside the desired economic band.

## Actuator correction logic

Because the dominant limiting factor is **cold stress**, the climate optimizer should weight temperature correction more strongly than the other variables.

A simple priority rule is:

[
w_T > w_{RH} > w_V
]

for this case.

So the controller behavior becomes:

### 1. If temperature is below 14 °C

This is the main correction case.

* increase heater
* reduce unnecessary damper opening
* keep cooler off
* avoid excessive air velocity if it increases convective cooling

Example:

* measured: (T=12.6^\circ C,\ RH=67%,\ V=0.8)
* action:

  * heater: increase
  * cooler: 0
  * damper: slightly close if safe

Possible command trend:

[
u_t = [u_h\uparrow,\ u_c=0,\ u_d\downarrow]
]

## 2. If temperature is inside 14–18 °C

Then temperature is acceptable, so the controller should avoid wasting energy.

* heater only as needed
* cooler off unless temperature drifts high
* damper adjusted mainly for humidity and air velocity

This is where the economic part matters: do not over-control when the process is already inside the profitable band.

## 3. If temperature rises above 18 °C

Even though the main issue is cold stress, overheating should still be corrected.

* reduce heater to zero
* open damper if that helps
* use cooler only if needed
* keep air velocity within 0.4–0.9 m/s

## 4. If humidity rises above 70%

Then the optimizer should ventilate more, but without creating extra cold stress.

So because cold stress is the current priority:

* first try moderate damper control
* do not over-ventilate if it drops temperature too much
* only use actions that keep temperature near the warm band

This is an important coupling:
humidity correction must be done without destroying the temperature objective.

## 5. If air velocity rises above 0.9 m/s

Since cold stress is dominant, too much air movement can worsen convective heat loss.

Then:

* reduce damper opening if possible
* avoid fan or cooling actions that increase air speed
* compensate with heater only if necessary

## A practical control objective

The climate optimizer can convert (x_2) into a low-level cost like:

[
J_t =
w_T \cdot d(T_t,[14,18])^2
+
w_{RH} \cdot d(RH_t,[55,70])^2
+
w_V \cdot d(V_t,[0.4,0.9])^2
+
w_u \cdot |\Delta u_t|^2
]

where (d(\cdot,\text{band})) is distance from the allowed band, and (\Delta u_t) penalizes aggressive actuator changes.

Because priority is cold-stress reduction, choose something like:

[
w_T = 10,\quad w_{RH}=4,\quad w_V=3
]

So temperature tracking matters most.

## How the feedback correction works step by step

Using your (x_2), the lower controller can run this cycle:

1. Read sensors:
   [
   z_t = {T_t,RH_t,V_t}
   ]

2. Read guidance:
   [
   x_2 = {T^{ref},RH^{ref},V^{ref},priority,limiting\ factor}
   ]

3. Compute deviations from the target bands

4. Weight the deviations according to the priority:

   * cold stress means temperature gets highest weight

5. Compute actuator corrections:

   * heater for low temperature
   * damper for humidity and air velocity balance
   * cooler only if upper temperature bound is exceeded

6. Apply actuator commands

7. Read sensors again after the next interval

8. Repeat until the next daily (x_2) arrives from BeefMPC-Guide

## Example with your output

Suppose sensors currently read:

```json
{
  "air_temperature_c": 12.8,
  "relative_humidity_pct": 74.0,
  "air_velocity_mps": 1.0
}
```

Compared with (x_2):

* temperature is too low
* humidity is too high
* air velocity is slightly too high

Because the priority is cold stress, the controller should not simply open the damper more to reduce humidity, since that may worsen cold stress.

A sensible correction is:

* heater: increase
* cooler: off
* damper: adjust carefully, only enough to reduce humidity without causing more cooling
* keep velocity from exceeding the upper air-speed band

So a command trend might be:

```json
{
  "heater_cmd": 0.62,
  "cooler_cmd": 0.0,
  "damper_cmd": 0.18
}
```

Then after some time, sensors may become:

```json
{
  "air_temperature_c": 14.7,
  "relative_humidity_pct": 69.0,
  "air_velocity_mps": 0.7
}
```

Now the process is inside the target bands, so the controller should reduce unnecessary actuation:

* heater: lower to holding level
* cooler: off
* damper: keep moderate

That is the correction process.

## Why this works

The important point is that (x_2) tells the climate optimizer:

* what ranges are biologically and economically preferred for the next 24 hours
* what limiting factor is currently hurting performance
* what expected biological benefit is associated with tracking those ranges

So the climate optimizer uses the sensors for **fast feedback correction**, and uses (x_2) for **economic direction**.

In your case, the meaning is:

* keep the barn in a moderately warm band
* avoid over-ventilation that increases cold stress
* use heater as the primary actuator
* use damper mainly as a secondary correction for humidity
* use cooler only if temperature exceeds the upper band

So (x_2) is effectively a **target-demand contract** for the lower controller.

A compact rule for this case is:

[
\text{if cold stress dominates, then}
\quad
\text{heater priority} > \text{damper priority} > \text{cooler priority}
]

and the controller keeps correcting until sensor measurements remain inside the target bands.
