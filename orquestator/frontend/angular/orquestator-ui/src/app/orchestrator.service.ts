import { Injectable } from '@angular/core';
import axios from 'axios';

@Injectable({ providedIn: 'root' })
export class OrchestratorService {
  private base = 'http://localhost:8000';

  async start(name: string): Promise<string> {
    const res = await axios.post<{ run_id: string }>(
      `${this.base}/start?name=${name}`
    );
    return res.data.run_id;
  }

  async status(runId: string): Promise<any> {
    const res = await axios.get<any>(`${this.base}/status/${runId}`);
    return res.data;
  }
}
