import {Dialog as SuiteDialog,type DialogProps} from '@cycling-suite/ui';
import {language} from './i18n';
export function Dialog(props:Omit<DialogProps,'locale'>){return <SuiteDialog {...props} locale={language==='en'?'en':'it'}/>}
