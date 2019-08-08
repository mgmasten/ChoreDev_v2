import { Component, ElementRef, Input, Renderer, ViewChild } from '@angular/core';

@Component({
  selector: 'chore-card',
  templateUrl: 'chore-card.html'
})
export class ChoreCardComponent {
  @Input() headerColor: string = 'green';
  @Input() textColor: string = 'blue';
  @Input() contentColor: string = '#FFF';
  @Input() dueDate: string;
  @Input() hasMargin: boolean = true;
  @Input() expanded: boolean = false;
  @Input() nickName: string;
  @Input() chore: string;
  @Input() isComplete: string;
  @Input() assignees: string;
  @Input() disabled: string;

  private complete;

  @ViewChild('accordionContent') elementView: ElementRef;

  viewHeight: number;

  constructor(public renderer: Renderer) { }

  ngAfterViewInit() {
    this.viewHeight = this.elementView.nativeElement.offsetHeight;

    if (!this.expanded) {
      this.renderer.setElementStyle(this.elementView.nativeElement, 'height', 0 + 'px');
    }
  }

  toggleAccordion() {
    this.expanded = !this.expanded;
    if (this.expanded) {
      this.renderer.setElementStyle(this.elementView.nativeElement, 'height', undefined);
    } else {
      this.renderer.setElementStyle(this.elementView.nativeElement, 'height', '0px');
    }
  }

}