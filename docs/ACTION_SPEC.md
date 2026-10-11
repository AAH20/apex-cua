# Action Specification: Atomic Contracts & Sub-Pixel Normalization

The Apex_CUA action subsystem eliminates blind action execution loops, ghost states, and resolution mismatch errors through formal contracts and affine transformations.

---

## 1. Sub-Pixel Invariant Affine Normalization

### 1.1 Resolution Invariance Principle
Agent models frequently hallucinate or miscalculate absolute pixel coordinates when desktop DPI scaling or screen resolutions change between training and runtime environments.

Apex_CUA standardizes all coordinate interactions onto a continuous unit plane:

$$\mathbf{p}_{\text{norm}} = (x_{\text{norm}}, y_{\text{norm}}) \in [0.0, 1.0] \times [0.0, 1.0]$$

### 1.2 Forward Affine Normalization
Given display width $W$, height $H$, hardware scale factor $S$ (e.g. $S = 2.0$ for Apple Retina), and viewport offsets $(\Delta_x, \Delta_y)$:

$$x_{\text{norm}} = \text{clamp}\left( \frac{x_{\text{screen}} - \Delta_x}{W \cdot S}, 0.0, 1.0 \right)$$

$$y_{\text{norm}} = \text{clamp}\left( \frac{y_{\text{screen}} - \Delta_y}{H \cdot S}, 0.0, 1.0 \right)$$

### 1.3 Inverse Screen Projection
When dispatching hardware events through Virtual HID injectors:

$$x_{\text{phys}} = (x_{\text{norm}} \cdot W \cdot S) + \Delta_x$$

$$y_{\text{phys}} = (y_{\text{norm}} \cdot H \cdot S) + \Delta_y$$

---

## 2. Atomic Action Contracts

### 2.1 State Transition Verification
An `ActionContract` defines an atomic interaction tuple:

$$\mathcal{C} = \langle \mathcal{I}, \mathcal{P}_{\text{pre}}, \mathcal{E}, \mathcal{P}_{\text{post}}, \mathcal{A}_{\text{comp}}, \tau \rangle$$

Where:
- $\mathcal{I}$: Action intent (e.g. click, type, key combo)
- $\mathcal{P}_{\text{pre}}$: Pre-condition predicate evaluated against system state
- $\mathcal{E}$: Virtual HID injection handler
- $\mathcal{P}_{\text{post}}$: Post-condition state assertion predicate
- $\mathcal{A}_{\text{comp}}$: Compensating action intent executed if $\mathcal{P}_{\text{post}}$ fails
- $\tau$: Maximum verification polling timeout

### 2.2 Transactional Action Journal
1. Intent $\mathcal{I}$ is recorded in the `ActionJournal` before event injection.
2. The compensating intent $\mathcal{A}_{\text{comp}}$ is pushed onto the rollback stack.
3. $\mathcal{E}(\mathcal{I})$ is dispatched via low-latency virtual HID.
4. State is polled up to timeout $\tau$.
5. If $\mathcal{P}_{\text{post}}$ evaluates to `True`, the transaction commits.
6. If timeout expires or an exception occurs, $\mathcal{A}_{\text{comp}}$ is popped in $O(1)$ and dispatched immediately, resetting the desktop state to an uncorrupted baseline.
