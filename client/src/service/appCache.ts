/**
 * Application Cache Service
 *
 * This service provides a uniform interface to both localStorage and
 * sessionStorage.
 *
 * NOTE - namespace clashing should not occur due to a prefix key set
 * in the main app.js module.
 *
 * @constructor AppCache
 */

interface ISession {
    token: string | null;
    username: string | null;
    userId: string | null;
    access_facility_id: string | null;
    access_facility_name: string | null;
    access_facility_type: string | null;
    access_facility_target: string | null;
    facility_parents: any[] | null;
    validator: number | null;
    lg: string | null; // Added for language preference
}

interface IAppCache {
    set(name: string, params: any): void;
    get(name: string): any;
    getSession(): ISession;
    clearSession(): void;
    setCurrentNode(nodeId:string):void
    getCurrentNode():String | null
}

function AppCache() {
    const service = {} as IAppCache;
    service.set = (name, params) => {
        const typ = typeof params;
        if (typ === 'object') {
            sessionStorage.setItem(name, JSON.stringify(params));
        } else {
            sessionStorage.setItem(name, `${params}`);
        }
    };

    service.get = (name) => {
        const result = sessionStorage.getItem(name);
        if (!result) return result;
        const isOBject = result.indexOf('{') !== -1 && result.indexOf('}');
        if (isOBject) {
            return JSON.parse(result);
        }
        return result;
    };

    service.clearSession = () => {
        localStorage.clear();
        sessionStorage.clear();
    }
    service.setCurrentNode = (nodeId:string) =>{
        localStorage.setItem('currentNode', nodeId);
    }
    service.getCurrentNode = () =>{
        return localStorage.getItem('currentNode');
    }
    service.getSession = (): ISession => {
        return {
            lg: localStorage.getItem('lg') || 'fr', // Default to French if not set
            token: localStorage.getItem('_ihris_token'),
            username: localStorage.getItem('_ihris_username'),
            userId: localStorage.getItem('_ihris_user_id'),
            access_facility_id: localStorage.getItem('_access_facility_id'),
            access_facility_name: localStorage.getItem('_access_facility_name'),
            access_facility_type: localStorage.getItem('_access_facility_type'),
            access_facility_target: localStorage.getItem('_access_facility_target'),
            facility_parents: (() => {
                const item = localStorage.getItem('_access_facility_parents');
                return item ? JSON.parse(item) : null;
            })(),
            validator: localStorage.getItem('validator') !== null ? Number(localStorage.getItem('validator')) : null
        };
    };

    return service;
}

const _AppCache = AppCache();
export default _AppCache;
