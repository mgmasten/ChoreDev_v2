import { Component, ElementRef, Input, Renderer, ViewChild } from '@angular/core';

@Component({
  selector: 'score-card',
  templateUrl: 'score-card.html'
})
export class ScoreCardComponent {
  @Input() headerColor: string = 'green';
  @Input() textColor: string = 'blue';
  @Input() contentColor: string = '#FFF';
  @Input() hasMargin: boolean = true;
  @Input() expanded: boolean = false;
  @Input() score: string;
  @Input() username: string;
  @Input() chore: string;
  @Input() isComplete: string;

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