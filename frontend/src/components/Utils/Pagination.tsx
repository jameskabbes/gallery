import React from 'react';
import { IoArrowBackSharp, IoArrowForwardSharp } from 'react-icons/io5';
import { Loader1 } from './Loader';

interface PaginationProps {
  loading: boolean;
  offset: number;
  setOffset: React.Dispatch<React.SetStateAction<PaginationProps['offset']>>;
  limit: number;
  setLimit: React.Dispatch<React.SetStateAction<PaginationProps['limit']>>;
  nCurrent: number;
  nTotal: number;
}

function Pagination(props: PaginationProps) {
  const leftDisabled = props.offset === 0 || props.loading;
  const rightDisabled =
    props.offset + props.limit >= props.nTotal || props.loading;

  return (
    <div className="flex flex-row items-center space-x-1">
      <span>
        {props.loading ? (
          <Loader1 className="inline" />
        ) : (
          <>
            {props.offset + 1}-{props.nCurrent + props.offset} of {props.nTotal}
          </>
        )}
      </span>
      <button
        disabled={leftDisabled}
        onClick={() =>
          props.setOffset((prev) => Math.max(0, prev - props.limit))
        }
      >
        <IoArrowBackSharp className={leftDisabled ? 'opacity-50' : ''} />
      </button>
      <button
        disabled={rightDisabled}
        onClick={() => props.setOffset((prev) => prev + props.limit)}
      >
        <IoArrowForwardSharp className={rightDisabled ? 'opacity-50' : ''} />
      </button>
    </div>
  );
}

export { Pagination };
