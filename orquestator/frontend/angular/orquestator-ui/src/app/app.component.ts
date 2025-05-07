import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WorkflowFormComponent } from './workflow-form/workflow-form.component';
import { WorkflowStatusComponent } from './workflow-status/workflow-status.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, WorkflowFormComponent, WorkflowStatusComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  runId = '';
  onStarted(id: string) {
    this.runId = id;
  }
  onReset() {
    this.runId = '';
  }
}
