import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { OrchestratorService } from '../orchestrator.service';

@Component({
  selector: 'app-workflow-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  templateUrl: './workflow-form.component.html',
  styleUrls: ['./workflow-form.component.css'],
})
export class WorkflowFormComponent {
  form: FormGroup;
  error = '';
  @Output() started = new EventEmitter<string>();

  constructor(private fb: FormBuilder, private svc: OrchestratorService) {
    this.form = this.fb.group({ name: ['deploy'] });
  }

  async submit() {
    this.error = '';
    try {
      const id = await this.svc.start(this.form.value.name);
      this.started.emit(id);
    } catch (err: any) {
      this.error = err.message || 'Error starting workflow';
    }
  }
}
