import { Component, ElementRef, Input, Renderer, ViewChild } from '@angular/core';

@Component({
  selector: 'profile-card',
  templateUrl: 'profile-card.html'
})
export class ProfileCardComponent {
  @Input() title: string;
  @Input() headerColor: string = 'green';
  @Input() textColor: string = 'blue';
  @Input() contentColor: string = '#FFF';
  @Input() hasMargin: boolean = true;
  @Input() expanded: boolean = false;
  @Input() username: string;
  @Input() email: string;
 
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
    const newHeight = this.expanded ? '250px' : '0px';
    this.renderer.setElementStyle(this.elementView.nativeElement, 'height', newHeight);
  }

}
