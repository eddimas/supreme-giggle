import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkflowStatusComponent } from './workflow-status.component';

describe('WorkflowStatusComponent', () => {
  let component: WorkflowStatusComponent;
  let fixture: ComponentFixture<WorkflowStatusComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WorkflowStatusComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WorkflowStatusComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
