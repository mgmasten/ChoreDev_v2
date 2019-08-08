import { Component, Input } from '@angular/core';

@Component({
  selector: 'burger-nav',
  templateUrl: 'burger-nav.html'
})
export class BurgerNavComponent {
  @Input() title: string;

}
