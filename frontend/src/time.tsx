import {TimeInput as SuiteTimeInput} from '@cycling-suite/ui';
import {language} from './i18n';
import type {ComponentProps} from 'react';
export {clock,parseClock,validTimes} from '@cycling-suite/ui';
export function TimeInput(props:Omit<ComponentProps<typeof SuiteTimeInput>,'locale'>){return <SuiteTimeInput {...props} locale={language==='en'?'en':'it'}/>}
