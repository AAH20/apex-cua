# Apex_CUA Diagram Repository (Diagram-Design Standard)

This repository houses the formal, fully annotated architectural diagrams for **Apex_CUA**, ensuring zero orphaned arrows, fully typed communication channels, and clear subsystem boundaries.

---

## 1. State Machine: Atomic Action Contract Lifecycle

```mermaid
stateDiagram-v2
    [*] --> PRE_CONDITION_EVAL: Intent Received (ActionContract)
    
    state PRE_CONDITION_EVAL {
        [*] --> CheckUIElementReady
        CheckUIElementReady --> AssertPrePredicate
        AssertPrePredicate --> PreApproved: Predicate == True
        AssertPrePredicate --> PreRejected: Predicate == False
    }

    PreRejected --> REJECTED_ABORT: Abort before HID Dispatch
    REJECTED_ABORT --> [*]

    PreApproved --> DISPATCH_VIRTUAL_HID: Push Compensating Action to Journal
    
    state DISPATCH_VIRTUAL_HID {
        [*] --> NormalizeCoords: Affine Transform to [0,1]
        NormalizeCoords --> InjectEvent: CoreGraphics / uinput
        InjectEvent --> EventAcknowledged: Sub-pixel Dispatch Complete
    }

    EventAcknowledged --> POST_CONDITION_AWAIT: Start Timeout Timer (tau)

    state POST_CONDITION_AWAIT {
        [*] --> PollState: 10ms Delta Sweep
        PollState --> AssertPostPredicate
        AssertPostPredicate --> TransitionSuccess: Predicate == True
        AssertPostPredicate --> TransitionTimeout: Clock > tau OR Predicate == False
    }

    TransitionSuccess --> COMMITTED_STATE: Pop Rollback Journal
    COMMITTED_STATE --> [*]: Emit TSSP State Diff

    TransitionTimeout --> ROLLBACK_EXECUTION: Trigger Compensating Stack
    
    state ROLLBACK_EXECUTION {
        [*] --> PopLIFOAction: Get Compensating Intent
        PopLIFOAction --> InjectReversal: Dispatch Escape / Cmd+Z / Focus Restore
        InjectReversal --> VerifyCleanState: Zero Dirty UI Invariant
    }

    VerifyCleanState --> RESTORED_FAULT: Raise ContractFaultException (State Clean)
    RESTORED_FAULT --> [*]
```

---

## 2. Shared-Memory Framebuffer (SHM-FB) Layout & Data Pipeline

```mermaid
flowchart TD
    subgraph POSIX_SHM["POSIX /dev/shm Zero-Copy Ring Buffer (8.29 MB)"]
        HEADER["Ring Header (64 Bytes)\n[Width: 1920 | Height: 1080 | Stride: 7680 | SeqNum: uint64]"]
        SLOT_0["Buffer Slot 0 (RGBA 1920x1080x4 = 8,294,400 Bytes)"]
        SLOT_1["Buffer Slot 1 (RGBA 1920x1080x4 = 8,294,400 Bytes)"]
        MUTEX["POSIX Atomic Spinlock / Mutex (0-Copy Sync)"]
    end

    subgraph PRODUCER["Compositor / Micro-LXC Sandbox"]
        COMP["Xvfb / Headless Wayland Compositor"]
        RENDER["Hardware Render Buffer (Metal / EGL)"]
        RENDER -->|mmap Direct Write| SLOT_0
        RENDER -->|mmap Direct Write| SLOT_1
    end

    subgraph CONSUMER["Apex_CUA Perception Engine"]
        READER["mmap Pointer Reader (1.03ms Map Latency)"]
        SLOT_0 -->|Zero Copy Pointer| READER
        SLOT_1 -->|Zero Copy Pointer| READER
        READER --> QT_DIFF["Spatial QuadTree (64-bit dHash)"]
        READER --> TILE_CROP["Micro-Tile Cropper (64x64 RGBA)"]
    end
```

---

## 3. Tokenized State Streaming Protocol (TSSP/1.0) Frame Structure

```mermaid
classDiagram
    class TSSPFrame {
        +string protocol_version = "TSSP/1.0"
        +uint64 sequence_number
        +float timestamp_ns
        +string session_id
        +AccessibilityDelta accessibility_delta
        +List~VisualTileDelta~ visual_deltas
        +ActiveContractStatus contract_status
        +to_json_ld() string
        +get_byte_size() int
    }

    class AccessibilityDelta {
        +string action = "upsert" | "remove"
        +string element_id
        +string role
        +string title
        +float x_norm
        +float y_norm
    }

    class VisualTileDelta {
        +string tile_id
        +int x
        +int y
        +int size = 64
        +uint64 dhash_64bit
        +string zlib_rgba_b64
    }

    class ActiveContractStatus {
        +string action_id
        +string status = "COMMITTED" | "ROLLED_BACK"
        +float latency_ms
    }

    TSSPFrame *-- AccessibilityDelta
    TSSPFrame *-- VisualTileDelta
    TSSPFrame *-- ActiveContractStatus
```

---

## 4. Voice Agent & Talking Avatar Full Integration Topology

```mermaid
flowchart TD
    subgraph INGRESS_VOICE["Speech Ingress (<30ms)"]
        MIC_IN["User Microphone / Audio Input"] --> WEBRTC_IN["WebRTC / WebSocket Audio Stream"]
        WEBRTC_IN --> SILERO["Silero VAD (<5ms Audio Framing)"]
        SILERO --> ASR_STREAM["Deepgram Nova-2 / Whisper Live (<25ms Streaming ASR)"]
    end

    subgraph CORE_MESH["Apex_CUA Cognitive Action Kernel (<15ms)"]
        ASR_STREAM --> INTENT_EXTRACT["Natural Language Intent Extractor"]
        INTENT_EXTRACT --> COGNITIVE_ROUTER["Cognitive Decision Router"]
        
        COGNITIVE_ROUTER -->|Deterministic GUI Action| JEV_ENGINE["Jev Solver (<0.002ms)"]
        COGNITIVE_ROUTER -->|Strategic Reasoning| LAYA_HOST["Laya System-1 Reflex (:8765)"]
        COGNITIVE_ROUTER -->|Policy Guardrail| CLEF_EDGE["Cloudflare Clef Router (<0.001ms)"]

        JEV_ENGINE --> ACTION_KERNEL["Action Contract Engine (Pre/Post Assertions)"]
        LAYA_HOST --> ACTION_KERNEL
        
        ACTION_KERNEL --> DESKTOP_EXEC["Native Virtual HID Injection (CoreGraphics)"]
        ACTION_KERNEL --> RESPONSE_GEN["Reflex Dialogue Generator"]
    end

    subgraph EGRESS_AVATAR["Speech & Avatar Egress (<150ms)"]
        RESPONSE_GEN --> TTS_STREAM["Cartesia Sonic / ElevenLabs Streaming TTS (<60ms TTFB)"]
        
        TTS_STREAM --> AUDIO_OUT["Opus Audio Playback (Speaker)"]
        TTS_STREAM --> VISEME_EXTRACT["Viseme & Phoneme Extractor"]
        
        VISEME_EXTRACT --> AVATAR_STREAM["Talking Avatar Engine (Dots / Simli / LiveKit)"]
        AVATAR_STREAM --> VIDEO_OUT["WebRTC Real-Time Avatar Video Stream (<80ms Sync)"]
    end

    DESKTOP_EXEC -->|State Updates| TSSP_OUT["TSSP State Streamer (11.53 Kbps)"]
```
