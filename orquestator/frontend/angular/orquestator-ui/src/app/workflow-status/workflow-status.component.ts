import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnInit,
  OnDestroy,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips'; // ← Aquí
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { OrchestratorService } from '../orchestrator.service';
import { interval, Subscription } from 'rxjs';
import { switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-workflow-status',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule, // ← IMPORTANTE: sin esto, mat-chip-list no existe
    MatIconModule,
    MatProgressBarModule,
  ],
  templateUrl: './workflow-status.component.html',
  styleUrls: ['./workflow-status.component.css'],
})
export class WorkflowStatusComponent implements OnInit, OnDestroy {
  @Input() runId!: string;
  @Output() reset = new EventEmitter<void>();
  run!: any;
  error = '';
  private sub!: Subscription;

  constructor(private svc: OrchestratorService) {}

  ngOnInit() {
    this.sub = interval(2000)
      .pipe(switchMap(() => this.fetchStatus()))
      .subscribe({
        next: () => {},
        error: (err) => {
          this.error = err.message;
          this.sub.unsubscribe();
        },
      });
    this.fetchStatus();
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  private async fetchStatus() {
    const data = await this.svc.status(this.runId);
    data.steps = data.steps.map((step: any) => {
      const start = step.started_at
        ? new Date(step.started_at).toLocaleTimeString()
        : '';
      const end = step.ended_at
        ? new Date(step.ended_at).toLocaleTimeString()
        : '';
      const duration =
        step.started_at && step.ended_at
          ? `${(
              (new Date(step.ended_at).getTime() -
                new Date(step.started_at).getTime()) /
              1000
            ).toFixed(1)}s`
          : '';
      return { ...step, startTime: start, endTime: end, duration };
    });
    this.run = data;
  }
}
