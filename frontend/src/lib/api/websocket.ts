import type { WSMessage } from "@/lib/types/api";

type ConnectionState = "connecting" | "connected" | "reconnecting" | "closed";

const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000, 30000];
const MAX_RECONNECT_ATTEMPTS = 5;

export class ReportWebSocket {
    private ws: WebSocket | null = null;
    private reportId: string;
    private token: string;
    private state: ConnectionState = "closed";
    private reconnectAttempts = 0;
    private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    private intentionallyClosed = false;

    private claimUpdateHandler: ((update: Extract<WSMessage, { type: "claim_update" }>) => void) | null = null;
    private completeHandler: ((result: Extract<WSMessage, { type: "report_complete" }>) => void) | null = null;
    private errorHandler: ((error: Extract<WSMessage, { type: "error" }>) => void) | null = null;
    private connectionChangeHandler: ((state: ConnectionState) => void) | null = null;

    constructor(reportId: string, token: string) {
        if (typeof window === "undefined") {
            throw new Error("ReportWebSocket is client-only");
        }
        this.reportId = reportId;
        this.token = token;
    }

    private setConnectionState(state: ConnectionState): void {
        this.state = state;
        this.connectionChangeHandler?.(state);
    }

    connect(): void {
        if (this.intentionallyClosed) return;

        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "wss://factanchor-api.onrender.com";
        const url = `${wsUrl}/ws/reports/${this.reportId}/stream?token=${this.token}`;

        this.setConnectionState("connecting");
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            this.reconnectAttempts = 0;
            this.setConnectionState("connected");
        };

        this.ws.onmessage = (event: MessageEvent) => {
            try {
                const msg = JSON.parse(event.data as string) as WSMessage | { type: "ping" };
                if (msg.type === "ping") return;

                switch (msg.type) {
                    case "claim_update":
                        this.claimUpdateHandler?.(msg);
                        break;
                    case "report_complete":
                        this.completeHandler?.(msg);
                        break;
                    case "error":
                        this.errorHandler?.(msg);
                        break;
                }
            } catch {
                // Ignore malformed messages
            }
        };

        this.ws.onclose = (event: CloseEvent) => {
            if (this.intentionallyClosed || event.code === 1000) {
                this.setConnectionState("closed");
                return;
            }
            this.scheduleReconnect();
        };

        this.ws.onerror = () => {
            // onclose will fire after this, which handles reconnection
        };
    }

    disconnect(): void {
        this.intentionallyClosed = true;
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        if (this.ws) {
            this.ws.close(1000);
            this.ws = null;
        }
        this.setConnectionState("closed");
    }

    private scheduleReconnect(): void {
        if (this.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
            this.errorHandler?.({
                type: "error",
                code: "WS_CONNECTION_FAILED",
                message: `Failed to reconnect after ${MAX_RECONNECT_ATTEMPTS} attempts`,
            });
            this.setConnectionState("closed");
            return;
        }

        const delay = RECONNECT_DELAYS[Math.min(this.reconnectAttempts, RECONNECT_DELAYS.length - 1)];
        this.reconnectAttempts++;
        this.setConnectionState("reconnecting");

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }

    onClaimUpdate(handler: (update: Extract<WSMessage, { type: "claim_update" }>) => void): this {
        this.claimUpdateHandler = handler;
        return this;
    }

    onComplete(handler: (result: Extract<WSMessage, { type: "report_complete" }>) => void): this {
        this.completeHandler = handler;
        return this;
    }

    onError(handler: (error: Extract<WSMessage, { type: "error" }>) => void): this {
        this.errorHandler = handler;
        return this;
    }

    onConnectionChange(handler: (state: ConnectionState) => void): this {
        this.connectionChangeHandler = handler;
        return this;
    }
}
